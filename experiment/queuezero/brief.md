# QueueZero — Stage 3 Controlled Architecture Benchmark

## Purpose

This is a fixed content brief for comparing presentation-generation architectures. Facts must remain identical across image-first, native/vector, and hybrid variants.

## Project

QueueZero is an AI-powered system that predicts congestion at university cafeterias and recommends the best dining location and time.

## Users

- university students
- cafeteria operators

## Problem

- students waste 15–30 minutes waiting at peak meal periods
- congestion is unpredictable
- operators struggle with staffing and food-preparation timing

## Solution

- computer vision estimates queue length
- historical + live data predicts waiting time
- student app recommends when and where to eat
- operator dashboard forecasts congestion

## Prototype evidence

- 3 cafeterias
- live demo
- prediction MAE: 3.8 minutes
- tested with 42 students
- 76% said they would use it weekly
- prototype built in 36 hours

## Business opportunity

- university licensing
- enterprise campus dining
- potential expansion into hospitals and large workplaces

## Competition

- Google Maps popular times
- manual cafeteria dashboards
- generic queue systems

## Differentiation

- real-time campus-specific prediction
- recommendation, not just monitoring
- student + operator interfaces

## Team

- 4 members

## Ask

Pilot with one university for one semester.

# Stage 3 slide subset

Only three slide types are required for the initial architecture experiment.

## S1 — Problem / Hook

Test visual impact, hierarchy, storytelling, and whether a rich first-impression slide requires full-slide image generation.

Required factual content:

- 15–30 minutes wasted at peak meal periods
- queue congestion is unpredictable
- operators also suffer from poor staffing/preparation timing

## S2 — How It Works

Test diagrams, connectors, vector freedom, and editable structural graphics.

Required conceptual flow:

1. camera / computer vision estimates queue length
2. historical + live data feed prediction
3. waiting time is predicted
4. student receives when/where recommendation
5. operator receives congestion forecast

## S3 — Validation / Traction

Test exact text/data fidelity, KPI rendering, and last-minute editability.

Required metrics:

- 3 cafeterias
- 3.8-minute prediction MAE
- 42 students tested
- 76% weekly-use intent
- built in 36 hours

# Architecture variants

Each slide must eventually be produced in three variants:

1. `image_first` — complete slide visual generated as a raster image
2. `native_vector` — editable PowerPoint/native and SVG-to-DrawingML objects, with no full-slide raster
3. `hybrid` — native text/data/structure plus bounded generated imagery where it materially improves visual quality

# Controlled edit tests

At minimum, test:

- change 76% to 81%
- change the headline
- replace a screenshot/image asset
- move one KPI/card
- reduce title size
- change the primary accent color
- delete one metric
- add a sponsor logo
- change diagram wording
- regenerate only a bounded hero visual without changing surrounding content

# Evidence rule

Do not declare an architecture superior based on screenshots alone. Preserve actual PPTX files and inspect their internal object composition where applicable.
