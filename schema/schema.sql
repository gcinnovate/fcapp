CREATE TABLE fcapp_user_roles (
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    descr text DEFAULT '',
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX fcapp_user_roles_idx1 ON fcapp_user_roles(name);

CREATE TABLE fcapp_user_role_permissions (
    id SERIAL NOT NULL PRIMARY KEY,
    user_role INTEGER NOT NULL REFERENCES fcapp_user_roles ON DELETE CASCADE ON UPDATE CASCADE,
    Sys_module TEXT NOT NULL, -- the name of the module - defined above this level
    sys_perms VARCHAR(16) NOT NULL,
    unique(sys_module,user_role)
);

CREATE TABLE fcapp_users (
    id bigserial NOT NULL PRIMARY KEY,
    user_role  INTEGER NOT NULL REFERENCES fcapp_user_roles ON DELETE RESTRICT ON UPDATE CASCADE, --(call agents, admin, service providers)
    firstname TEXT NOT NULL DEFAULT '',
    lastname TEXT NOT NULL DEFAULT '',
    username TEXT NOT NULL UNIQUE,
    telephone TEXT NOT NULL DEFAULT '', -- acts as the username
    password TEXT NOT NULL, -- blowfish hash of password
    email TEXT NOT NULL DEFAULT '',
    allowed_ips TEXT NOT NULL DEFAULT '127.0.0.1;::1', -- semi-colon separated list of allowed ip masks
    denied_ips TEXT NOT NULL DEFAULT '', -- semi-colon separated list of denied ip masks
    failed_attempts TEXT DEFAULT '0/'||to_char(now(),'yyyymmdd'),
    transaction_limit TEXT DEFAULT '0/'||to_char(now(),'yyyymmdd'),
    is_active BOOLEAN NOT NULL DEFAULT 't',
    is_system_user BOOLEAN NOT NULL DEFAULT 'f',
    last_login TIMESTAMPTZ,
    last_passwd_update TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX fcapp_users_idx1 ON fcapp_users(telephone);
CREATE INDEX fcapp_users_idx2 ON fcapp_users(username);

CREATE TABLE fcapp_audit_log (
        id BIGSERIAL NOT NULL PRIMARY KEY,
        logtype VARCHAR(32) NOT NULL DEFAULT '',
        actor TEXT NOT NULL,
        action text NOT NULL DEFAULT '',
        remote_ip INET,
        detail TEXT NOT NULL,
        created_by INTEGER REFERENCES fcapp_users(id), -- like actor id
        created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX fcapp_au_idx1 ON fcapp_audit_log(created);
CREATE INDEX fcapp_au_idx2 ON fcapp_audit_log(logtype);
CREATE INDEX fcapp_au_idx4 ON fcapp_audit_log(action);

INSERT INTO fcapp_user_roles(name, descr)
VALUES('Administrator','For the Administrators'), ('API User', 'For the API Users');

INSERT INTO fcapp_user_role_permissions(user_role, sys_module,sys_perms)
VALUES
        ((SELECT id FROM fcapp_user_roles WHERE name ='Administrator'),'Users','rw');

INSERT INTO fcapp_users(firstname,lastname,username,telephone,password,email,user_role,is_system_user)
VALUES
        ('Samuel','Sekiwere','admin', '+256753475676', crypt('admin',gen_salt('bf')),'sekiskylink@gmail.com',
        (SELECT id FROM fcapp_user_roles WHERE name ='Administrator'),'t'),
        ('Ivan','Muguya','ivan', '+256756253430', crypt('ivan',gen_salt('bf')),'ivanupsons@gmail.com',
        (SELECT id FROM fcapp_user_roles WHERE name ='API User'),'t');


CREATE OR REPLACE FUNCTION fcapp_has_msisdn(contactid INT) RETURNS BOOLEAN AS
$delim$
    DECLARE
        c_id INTEGER;
    BEGIN
        SELECT id INTO c_id FROM contacts_contacturn WHERE contact_id = contactid;
        IF FOUND THEN
            RETURN TRUE;
        END IF;
        RETURN FALSE;
    END;
$delim$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fcapp_has_hoh_msisdn(contactid INT) RETURNS BOOLEAN AS
$delim$
    DECLARE
        c_id INTEGER;
    BEGIN
        SELECT id INTO c_id FROM values_value WHERE contact_id = contactid
            AND contact_field_id = (SELECT id FROM contacts_contactfield WHERE label = 'HoH MSISDN');
        IF FOUND THEN
            RETURN TRUE;
        END IF;
        RETURN FALSE;

    END;
$delim$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fcapp_get_secondary_receivers(contact text, OUT contact_id int, OUT name text, OUT uuid text,
    OUT msisdn text, OUT contact_field int, OUT has_msisdn BOOLEAN, OUT has_hoh_msisdn BOOLEAN)
    RETURNS SETOF record
AS $$
    WITH t AS
        (SELECT contact_id, string_value, contact_field_id FROM values_value
            WHERE
            contact_field_id IN (SELECT id FROM contacts_contactfield WHERE label IN('HoH MSISDN', 'SecReceiver MSISDN'))
            AND substring(reverse(string_value), 0, 9) = substring(reverse(contact), 0, 9)
        )
            SELECT a.id, a.name, a.uuid, t.string_value, t.contact_field_id,
                fcapp_has_msisdn(a.id) AS has_msisdn, fcapp_has_hoh_msisdn(a.id) AS has_hoh_msisdn
            FROM contacts_contact a, t
            WHERE t.contact_id = a.id;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION fcapp_get_registered_contact_details(contact text, registred_by text, OUT contact_id int, OUT name text, OUT uuid text,
    OUT msisdn text, OUT contact_field int, OUT has_msisdn BOOLEAN)
    RETURNS SETOF record
AS $$
    WITH t AS
        (SELECT contact_id, string_value, contact_field_id FROM values_value
            WHERE
            contact_field_id IN (SELECT id FROM contacts_contactfield WHERE label IN('Registered By'))
            AND substring(reverse(string_value), 0, 9) = substring(reverse(registred_by), 0, 9)
        )
            SELECT a.id, a.name, a.uuid, t.string_value, t.contact_field_id,
                fcapp_has_msisdn(a.id) AS has_msisdn
            FROM contacts_contact a, t, contacts_contacturn b
            WHERE t.contact_id = a.id AND a.id = b.contact_id AND substring(reverse(b.path), 0, 9) = substring(reverse(contact), 0, 9);
$$ LANGUAGE SQL;



CREATE VIEW fcapp_contact_fields_view AS
SELECT
    a.id, a.name,
    b.string_value AS dob_child_1,
    c.string_value AS dob_child_2,
    d.string_value AS dob_child_3,
    b.id AS dob1_id,
    c.id AS dob2_id,
    d.id AS dob3_id

FROM
    contacts_contact a
    LEFT OUTER JOIN values_value b ON (a.id = b.contact_id AND b.contact_field_id = 20)
    LEFT OUTER JOIN values_value c ON (a.id = c.contact_id AND c.contact_field_id = 21)
    LEFT OUTER JOIN values_value d ON (a.id = d.contact_id AND d.contact_field_id = 22);

CREATE TABLE fcapp_flow_data(
    id BIGSERIAL PRIMARY KEY NOT NULL,
    msisdn TEXT NOT NULL DEFAULT '',
    contact_uuid TEXT NOT NULL DEFAULT '',
    district INTEGER REFERENCES fcapp_locations(id),
    facility TEXT NOT NULL DEFAULT '',
    facilityuid TEXT NOT NULL DEFAULT '',
    subcounty TEXT,
    parish TEXT,
    village TEXT,
    report_type VARCHAR(16),
    week VARCHAR(8),
    month VARCHAR(8),
    quarter TEXT NOT NULL DEFAULT '',
    year INTEGER NOT NULL,
    "values" JSONB,
    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION add_node(treeid INT, node_name TEXT, p_id INT) RETURNS BOOLEAN AS --p_id = id of node where to add
$delim$
    DECLARE
    new_lft INTEGER;
    lvl INTEGER;
    dummy TEXT;
    node_type INTEGER;
    child_type INTEGER;
    BEGIN
        IF node_name = '' THEN
            RAISE NOTICE 'Node name cannot be empty string';
            RETURN FALSE;
        END IF;
        SELECT level INTO lvl FROM fcapp_locationtype WHERE id = (SELECT type_id FROM fcapp_locations WHERE id = p_id);
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Cannot add node: failed to find level';
        END IF;
        SELECT rght, type_id INTO new_lft, node_type FROM fcapp_locations WHERE id =  p_id AND tree_id = treeid;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'No such node id= % ', p_id;
        END IF;

        SELECT id INTO child_type FROM fcapp_locationtype WHERE level = lvl + 1 AND tree_id = tree_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'You cannot add to root node';
        END IF;

        SELECT name INTO dummy FROM fcapp_locations WHERE name = node_name
            AND tree_id = treeid AND type_id = child_type AND tree_parent_id = p_id;
        IF FOUND THEN
            RAISE NOTICE 'Node already exists : %', node_name;
            RETURN FALSE;
        END IF;

        UPDATE fcapp_locations SET lft = lft + 2 WHERE lft > new_lft AND tree_id = treeid;
        UPDATE fcapp_locations SET rght = rght + 2 WHERE rght >= new_lft AND tree_id = treeid;
        INSERT INTO fcapp_locations (name, lft, rght, tree_id,type_id, tree_parent_id)
        VALUES (node_name, new_lft, new_lft+1, treeid, child_type, p_id);
        RETURN TRUE;
    END;
$delim$ LANGUAGE plpgsql;
