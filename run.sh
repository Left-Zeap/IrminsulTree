#!/bin/bash
echo "Starting Genshin Knowledge Graph (Standalone)..."
cd "$(dirname "$0")"
streamlit run app.py
