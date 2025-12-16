# Project 29 – Fraud Detection and Claims Monitoring in Health Insurance

## 📋 Description
Built an advanced Excel-based fraud detection dashboard using healthcare insurance claims data. The dashboard leverages pivot tables, charts, slicers, and DAX to monitor claims and identify fraudulent patterns across procedures, hospitals, and demographics.

## 🎯 Objective
To analyze health insurance claim trends and uncover potential fraud risks using dynamic visuals and metrics.

## 🗃️ Datasets Used
1. `tblClaims` – Claim ID, procedure codes, hospital names, costs, fraud flag
2. `tblPolicyholders` – Demographics (age, gender, region, policy type)
3. `tblProcedure_Codes` – Procedure code descriptions
4. `tblHospitals` – Hospital names and IDs

## 🧠 Excel Features Used
- Pivot Tables:
  1. Total Claims Summary by Region
  2. Fraud Rate by Gender
  3. Claims by Procedure
  4. Fraud Rate by Procedure Code
  5. Fraud Rate by Region
  6. Fraud Rate by Hospital
- Charts:
  - Column, Bar, Pie, and Line Charts for visual trends
- Slicers:
  - Region, Gender, Procedure Code, Hospital Name, Fraud Flag
- DAX Measure:
  - `Fraud Rate = DIVIDE(SUM(tblClaims[Fraud_Flag]), COUNT(tblClaims[Claim_ID]))`

## 📈 Key Insights
- Certain hospitals and regions show elevated fraud risk
- Gender and procedure type impact likelihood of fraudulent claims
- Specific procedures are more frequently flagged as suspicious

## ✅ Benefits
- Detects high-risk claims in real time
- Improves fraud prevention strategies
- Helps insurers allocate auditing resources effectively

## 📁 File
- `Health_Insurance_Fraud_Dashboard.xlsx`
