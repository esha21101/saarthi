CREATE TABLE customers (
    id     SERIAL PRIMARY KEY,
    full_name  TEXT NOT NULL,
    phone   TEXT NOT NULL UNIQUE,
    email   TEXT NOT NULL,
    dob     DATE NOT NULL,
    address  TEXT NOT NULL
);

CREATE TABLE loans (
    id  SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES customers(id),
    loan_type  TEXT NOT NULL,
    outstanding_amount  NUMERIC(12, 2) NOT NULL,
    emi_amount  NUMERIC(12, 2) NOT NULL,
    next_due_date  DATE ,
    status  TEXT NOT NULL

);

CREATE TABLE payments(
    id SERIAL PRIMARY KEY,
    loan_id INT NOT NULL REFERENCES loans(id),
    amount  numeric(12,2) NOT NULL,
    due_date  DATE NOT NULL,
    paid_date  DATE,
    status  TEXT NOT NULL

);

CREATE TABLE statements(
    id  SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES customers(id),
    loan_id INT NOT NULL REFERENCES loans(id),
    period  TEXT NOT NULL,
    sent_to TEXT NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE call_logs(
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL, 
    customer_id INT REFERENCES customers(id), 
    event  TEXT NOT NULL , 
    details JSONB, 
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );