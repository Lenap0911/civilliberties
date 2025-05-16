-- Create the countries table
CREATE TABLE countries (
    country_id INTEGER PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    country_code CHAR(2) NOT NULL UNIQUE
);

-- Create the trust_levels table
CREATE TABLE trust_levels (
    trust_id INTEGER PRIMARY KEY,
    country_id INTEGER,
    year INTEGER NOT NULL,
    trust_score DECIMAL(4,2),  -- Trust in legal system score
    response_count INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    UNIQUE(country_id, year)
);

-- Create the freedom_scores table
CREATE TABLE freedom_scores (
    freedom_id INTEGER PRIMARY KEY,
    country_id INTEGER,
    year INTEGER NOT NULL,
    freedom_score DECIMAL(4,2),  -- Overall freedom score
    civil_liberties_score DECIMAL(4,2),  -- Overall civil liberties score (max 60)
    freedom_expression_belief DECIMAL(4,2),  -- Freedom of Expression and Belief (max 16)
    associational_rights DECIMAL(4,2),  -- Associational and Organizational Rights (max 12)
    rule_of_law DECIMAL(4,2),  -- Rule of Law (max 16)
    personal_autonomy DECIMAL(4,2),  -- Personal Autonomy and Individual Rights (max 16)
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    UNIQUE(country_id, year)
);


