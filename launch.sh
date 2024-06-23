#!/bin/bash

# Costruisci le immagini Docker per Alice e Bob
docker-compose build

# Avvia i container
docker-compose up -d
