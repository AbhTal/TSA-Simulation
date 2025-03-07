# TSA-Simulation

# ✈️ TSA Airport Line Simulation  
**Course:** CS_4632_W01  
**Author:** [Your Name]  
**Milestone:** Model Implementation  

## 📌 Project Overview  
This project simulates the **TSA airport security checkpoint process** using **SimPy**, a Python-based discrete-event simulation library. The model is designed to analyze **queue times, TSA agent workload, and passenger flow efficiency** under different conditions.  

## 🎯 Implementation Goals  
✅ Simulate passenger arrivals at TSA checkpoints.  
✅ Model **Regular vs. PreCheck passengers** with different screening times.  
✅ Implement **TSA agents processing passengers** at security lanes.  
✅ Track **queue times, throughput, and secondary screenings**.  
✅ Allow **adjustable parameters** for peak hours, staffing levels, and efficiency testing.  

## 🏗️ Simulation Structure  
- **Passenger**: Arrives at security, joins a queue, gets screened.  
- **QueueSystem**: Manages **Regular and PreCheck** passenger queues.  
- **Checkpoint**: Represents security lanes where TSA agents process travelers.  
- **TSAAgent**: Screens passengers and determines if secondary screening is needed.  
- **Simulation**: Runs the model for a set duration, collecting performance metrics.  

## ⚙️ Setup & Running the Simulation  
### 1️⃣ **Install Dependencies**  
Ensure you have **Python 3.x** and install required libraries:  
```bash
pip install simpy matplotlib pandas
