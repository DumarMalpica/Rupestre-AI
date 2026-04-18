-- Inicialización de la base de datos Rupestre AI
-- Extensión geoespacial PostGIS

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    municipality VARCHAR(100),
    location GEOGRAPHY(POINT, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    record_id VARCHAR(20) UNIQUE NOT NULL,
    motif_count INT DEFAULT 0,
    cultural_interpretation TEXT,
    reconstruction_applied BOOLEAN DEFAULT FALSE,
    ficha_pdf_path VARCHAR(500),
    ficha_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sites_location ON sites USING GIST(location);
CREATE INDEX idx_records_record_id ON records(record_id);
