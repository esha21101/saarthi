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