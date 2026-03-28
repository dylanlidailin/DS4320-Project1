# DS 4320 Spring 2026 — Project 1: Relational Model

**Goal:** Solve a problem by creating a fully established secondary data set, D1, using the relational model.

## Process

1. Select a general problem from the list below.
2. Refine that general problem into a specific problem.
3. Develop a specific solution.

---

## General problems (pick one to refine)

> These are starting points, not final topics. Refine into a **specific** problem.

- [ ] 1. Detecting credit card fraud
- [ ] 2. Predicting loan default risk
- [ ] 3. Forecasting stock prices
- [ ] 4. Forecasting global climate change
- [ ] 5. Detecting AI generated images/text/etc.
- [ ] 6. Projecting athletic performance
- [ ] 7. Predicting sports game outcomes
- [ ] 8. Clinical drug trials
- [ ] 9. Predicting hospital readmission risk
- [ ] 10. Allocating emergency response resources
- [ ] 11. Forecasting energy demand
- [ ] 12. Predicting wildfire risk
- [ ] 13. Predicting air quality
- [ ] 14. Recommending content (e.g. Netflix)
- [ ] 15. Detecting online bots
- [ ] 16. Predicting election results
- [ ] 17. Other (after office hours discussion)

---

## Rubric checklist

### General

- [ ] (1 pt) Materials are submitted on time
- [ ] (4 pts) Materials are submitted as a well organized GitHub repository
- [ ] (1 pt) Data are stored in a UVA OneDrive folder and linked in the GitHub readme
- [ ] (4 pts) README is a markdown file that makes all materials easy to find and access (in root folder of project; header structure as indicated in this rubric)

### Coding standards

- [ ] (1 pt) Project is written in Python, Markdown, and SQL
- [ ] (1 pt) All code runs without major errors
- [ ] (1 pt) Code is commented inline to explain every class/function
- [ ] (1 pt) Python includes proper error handling
- [ ] (1 pt) Python includes logging to log files

### Project details — L1 header

- [ ] (1 pt) Title — `DS 4320 Project 1:` followed by your project title (L1 line)
- [ ] (2 pts) Executive Summary — short paragraph explaining the contents of the repository in executive form
- [ ] (1 pt) Name
- [ ] (1 pt) NetID
- [ ] (1 pt) DOI — create a DOI for your project
- [ ] (1 pt) Press Release — link to press release
- [ ] (1 pt) Data — link to data folder
- [ ] (1 pt) Pipeline — link to pipeline files
- [ ] (1 pt) License — state name of license here and link to the file in the top level of the repository (normal GitHub conventions)

### Problem definition — L2 header

- [ ] (3 pts) State the initial general problem and refined specific problem statement
- [ ] (3 pts) One paragraph explaining the rationale for that refinement
- [ ] (3 pts) One paragraph explaining the motivation for the project
- [ ] (1 pt) Headline of Press Release and link to separate markdown file containing the press release

### Domain exposition — L2 header

- [ ] (2 pts) Terminology — table summarizing jargon, KPIs, etc.
- [ ] (2 pts) Paragraph explaining the domain the project lives in
- [ ] (1 pt each, max 5) Background reading — separate folder with copies of articles, blog posts, etc. (helps reader understand the domain)
  - [ ] Reading 1
  - [ ] Reading 2
  - [ ] Reading 3
  - [ ] Reading 4
  - [ ] Reading 5
- [ ] (1 pt) Table — summary of readings (one row per item: title, brief description, link to file in folder)

### Data creation — L2 header

- [ ] (2 pts) Paragraph or two explaining the raw data acquisition process (provenance)
- [ ] (3 pts) Code table — code used to create the data (one row per file: brief description, link to code in repo)
- [ ] (1 pt) Bias identification — how bias could be/was introduced in data collection
- [ ] (1 pt) Bias mitigation — how biases can be handled/quantified/accounted for in analysis
- [ ] (3 pts) Rationale for critical decisions, especially judgement calls, and places that can introduce/mitigate uncertainty

### Metadata — L2 header

- [ ] (3 pts) Schema — ER diagram at the logical level
- [ ] (1 pt) Data table — all tables in the dataset (one line per table: brief description, link to CSV)
- [ ] (3 pts) Data dictionary — one row per feature: name, data type, description, example
- [ ] (3 pts) Data dictionary — quantification of uncertainty for numerical features

### Press release — separate markdown file

- [ ] (2 pts) Headline — L1 header
- [ ] (2 pts) Hook — L2 header — short, holds attention, explains the motivation
- [ ] (2 pts) Problem Statement — L2 header — current state of affairs, your specific problem
- [ ] (2 pts) Solution Description — L2 header — high level for end-user, not technical
- [ ] (2 pts) Chart — L2 header — visualizes your data and supports your solution

### Data — UVA OneDrive folder

- [ ] (1 pt) Constructed using the relational model
- [ ] (4 pts) Minimum of 4 tables
- [ ] (1 pt) Storage — every table as a CSV file
- [ ] (1 pt) Scale — data files total more than one KB
- [ ] (1 pt) Scale — data files total more than one MB
- [ ] (1 pt) Scale — data files total more than one GB
- [ ] (1 pt) Scale — data files stored in Parquet format

### Problem solution pipeline — separate files

- [ ] (1 pt) File 1: pipeline in a Jupyter notebook
- [ ] (1 pt) File 2: notebook also saved as a Markdown file
- [ ] (1 pt) Data preparation — load CSV files into a database with DuckDB using Python
- [ ] (1 pt) Query — queries to prepare your solution
- [ ] (1 pt) Solution analysis — implement a model
- [ ] (1 pt) Analysis rationale — explain decisions in your analysis process
- [ ] (1 pt) Analysis complexity — utilize ML/AI taught in DS 3021/4021
- [ ] (1 pt) Visualize results — visualization of results
- [ ] (1 pt) Visualization rationale — explain decisions in your visualization process
- [ ] (1 pt) Visualization is publication quality
- [ ] (5 pts) Pipeline solves the problem

---

**Total: 100 points**

_Source: converted from `project-1-rubric.pdf` for personal tracking._
