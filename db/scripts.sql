CREATE DATABASE ucss;
USE ucss;

CREATE TABLE IF NOT EXISTS usuarios (
    idUser INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    codigo VARCHAR(20) UNIQUE,
    facultad VARCHAR(100),
    carrera VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embeddings (
	idEmb INT AUTO_INCREMENT PRIMARY KEY,
    idUser INT NOT  NULL,
    content BLOB NOT NULL,
    FOREIGN KEY (idUser) REFERENCES usuarios(idUser)
);

SELECT * FROM usuarios;