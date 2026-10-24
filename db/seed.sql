INSERT INTO customers (full_name, phone, email, dob, address) VALUES
('Anya Roger', '8964384771', 'anya22@yahoo.com', '1993-11-27', 'New Emblem Street escape 24'),
('Takasha Timber', '9644387214', 'Takashasha234@dwight.com', '1989-06-07', 'Nem show Street port twig 187'),
('Shinhara Pakeshu', '7774889494', 'Shinu@gkom.com', '1984-05-19', 'Acoitar Dune of Street number 731');

INSERT INTO loans (customer_id, loan_type, outstanding_amount, emi_amount, next_due_date, status) VALUES
(1, 'home loan', 1240070, 30000, '2026-11-12', 'active'),
(1, 'personal loan', 85000, 4500, '2026-11-20', 'active'),
(2, 'personal loan', 200000, 8000, '2026-11-05', 'active'),
(3, 'two-wheeler loan', 0, 0, NULL, 'closed');