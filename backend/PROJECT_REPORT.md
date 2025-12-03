# Zero-Trust Anomaly Detection System

## Project Report

**Project Title:** Zero-Trust Anomaly Detection in Authentication Logs  
**Date:** November 2024  
**Version:** 1.0

---

## Executive Summary

This report documents the development and implementation of a Zero-Trust Anomaly Detection System designed to identify suspicious authentication behaviors in real-time. The project successfully delivered a machine learning-based solution that detects anomalies such as impossible travel, off-hours logins, unusual resource access, and large data transfers using a combination of unsupervised learning models (Isolation Forest, One-Class SVM, and Autoencoder).

The system achieved a 59-63% accuracy rate across different models, with the Isolation Forest model demonstrating the best balance of precision and recall. The implementation includes a real-time REST API, interactive dashboard, and automated email alerting capabilities, providing a comprehensive security monitoring solution.

**Key Achievements:**

- Successfully implemented three ML models for anomaly detection
- Developed real-time prediction API with sub-second response times
- Created interactive dashboard for security analysts
- Integrated automated alerting system
- Achieved operational deployment readiness

---

## 1. Analysis of the Initial Problem

### 1.1 Problem Statement

Organizations face increasing cybersecurity threats from sophisticated attackers who exploit authentication systems to gain unauthorized access. Traditional security approaches rely on perimeter defenses and signature-based detection, which are insufficient against modern threats such as:

- **Credential Theft and Account Takeover:** Attackers use stolen credentials to access systems, appearing as legitimate users
- **Insider Threats:** Malicious or compromised insiders with valid credentials
- **Advanced Persistent Threats (APTs):** Long-term, stealthy attacks that evade traditional detection
- **Zero-Day Exploits:** Unknown attack patterns that bypass signature-based systems

### 1.2 Current State Analysis

**Existing Challenges:**

1. **Reactive Security Posture:** Traditional systems detect threats only after they occur, leading to delayed response times
2. **High False Positive Rates:** Rule-based systems generate numerous false alarms, causing alert fatigue
3. **Limited Behavioral Analysis:** Systems focus on known attack patterns rather than behavioral anomalies
4. **Manual Investigation Overhead:** Security teams spend significant time investigating false positives
5. **Lack of Real-Time Capabilities:** Batch processing delays threat detection and response

**Data Characteristics:**

- Dataset: 50,000 authentication events
- Anomaly Rate: ~40% (20,241 anomalies out of 50,000 events)
- Anomaly Types: 16 distinct categories including:
  - Impossible travel
  - Off-hours login
  - Multiple failed logins
  - Large data transfer
  - Unusual resource access
  - Combinations of the above

### 1.3 Business Impact

**Quantifiable Risks:**

- **Mean Time to Detection (MTTD):** Without automated detection, threats may go undetected for days or weeks
- **Data Breach Costs:** Average cost of a data breach exceeds $4.45 million (2023 IBM Security Report)
- **Operational Disruption:** Security incidents cause downtime and productivity loss
- **Compliance Violations:** Failure to detect and respond to threats can result in regulatory penalties

**Qualitative Risks:**

- Reputation damage from security breaches
- Loss of customer trust
- Intellectual property theft
- Competitive disadvantage

### 1.4 Solution Requirements

The solution needed to address:

1. **Real-Time Detection:** Identify anomalies as they occur, not in retrospect
2. **Zero-Trust Architecture:** Treat all events as potentially suspicious until verified
3. **Explainability:** Provide clear reasoning for anomaly classifications
4. **Scalability:** Handle high-volume authentication events
5. **Integration:** Work with existing security infrastructure
6. **Usability:** Enable security analysts to quickly investigate and respond

---

## 2. Discussion of Improvement Opportunities

### 2.1 Model Performance Enhancements

**Current Performance:**

- Isolation Forest: 59% accuracy, 0.59 F1-score
- One-Class SVM: 59% accuracy, 0.59 F1-score
- Autoencoder: 63% accuracy, but low anomaly recall (10%)

**Improvement Opportunities:**

1. **Ensemble Methods**

   - Combine predictions from multiple models using voting or stacking
   - Expected improvement: 5-10% accuracy increase
   - Implementation complexity: Medium

2. **Feature Engineering**

   - Add temporal features (time since last login, login frequency)
   - Include user behavior baselines (average bytes transferred per user)
   - Geographic features (distance from previous location)
   - Expected improvement: 8-15% accuracy increase
   - Implementation complexity: Low-Medium

3. **Hyperparameter Optimization**

   - Systematic grid search or Bayesian optimization
   - Fine-tune contamination rates, kernel parameters, and neural network architecture
   - Expected improvement: 3-7% accuracy increase
   - Implementation complexity: Medium

4. **Advanced Deep Learning Models**
   - LSTM/GRU for sequence modeling of user behavior
   - Transformer-based models for complex pattern recognition
   - Expected improvement: 10-20% accuracy increase
   - Implementation complexity: High

### 2.2 System Architecture Improvements

**Current Limitations:**

- Kafka integration is optional and may not be available
- No persistent storage for historical predictions
- Limited model versioning and A/B testing capabilities

**Improvement Opportunities:**

1. **Database Integration**

   - Store all predictions and events in a time-series database (InfluxDB, TimescaleDB)
   - Enable historical analysis and model retraining
   - Implementation complexity: Medium

2. **Model Versioning and Deployment**

   - Implement MLflow or similar for model registry
   - Enable canary deployments and gradual rollouts
   - A/B testing framework for model comparison
   - Implementation complexity: Medium-High

3. **Enhanced Streaming Architecture**

   - Guaranteed Kafka integration with error handling
   - Event replay capabilities for model retraining
   - Dead letter queue for failed predictions
   - Implementation complexity: Medium

4. **Microservices Architecture**
   - Separate model serving, preprocessing, and alerting services
   - Independent scaling of components
   - Better fault isolation
   - Implementation complexity: High

### 2.3 Operational Improvements

**Current Gaps:**

- Manual model retraining process
- Limited monitoring and observability
- No automated model drift detection

**Improvement Opportunities:**

1. **Automated Model Retraining Pipeline**

   - Scheduled retraining on new data
   - Automated feature drift detection
   - Model performance monitoring
   - Implementation complexity: Medium-High

2. **Comprehensive Monitoring**

   - Real-time model performance metrics
   - Prediction latency tracking
   - Alert volume and false positive rate monitoring
   - Implementation complexity: Medium

3. **Model Explainability Enhancement**

   - SHAP integration already present, but can be expanded
   - LIME for local explanations
   - Counterfactual explanations
   - Implementation complexity: Low-Medium

4. **Integration with Security Orchestration**
   - SOAR (Security Orchestration, Automation, and Response) integration
   - Automated response actions (account lockout, IP blocking)
   - SIEM integration for centralized logging
   - Implementation complexity: High

### 2.4 User Experience Improvements

**Current State:**

- Dashboard provides good visualization but could be enhanced
- Limited filtering and search capabilities
  - No bulk operations for analysts

**Improvement Opportunities:**

1. **Advanced Dashboard Features**

   - Real-time streaming updates without manual refresh
   - Customizable alert rules and thresholds
   - User-specific dashboards and saved filters
   - Implementation complexity: Medium

2. **Investigation Workflow Tools**

   - Case management system for tracking investigations
   - Collaboration features for security teams
   - Integration with ticketing systems
   - Implementation complexity: Medium-High

3. **Mobile Application**
   - Mobile alerts and basic dashboard access
   - Push notifications for critical anomalies
   - Implementation complexity: Medium

---

## 3. Business Case for Identified Improvements

### 3.1 Financial Justification

**Cost-Benefit Analysis:**

**Investment Required:**

- Development resources: 3-6 months of engineering time
- Infrastructure: Additional compute for model training and serving (~$500-2,000/month)
- Third-party tools: MLflow, monitoring tools (~$200-500/month)
- **Total Estimated Investment: $50,000 - $150,000**

**Expected Benefits:**

1. **Reduced Security Incident Costs**

   - Current: Average detection time of 7-14 days
   - Improved: Real-time detection reduces MTTD to minutes
   - **Savings: $200,000 - $500,000 per prevented breach**

2. **Operational Efficiency**

   - Reduced false positive investigation time: 20-30 hours/week saved
   - Automated alerting reduces manual monitoring: 15-20 hours/week saved
   - **Annual Savings: $150,000 - $250,000 in labor costs**

3. **Compliance and Risk Mitigation**
   - Reduced risk of regulatory fines
   - Improved audit trail and reporting
   - **Value: $50,000 - $200,000 in avoided penalties**

**ROI Calculation:**

- **Total Annual Benefits: $400,000 - $950,000**
- **Total Investment: $50,000 - $150,000**
- **ROI: 267% - 1,800%**
- **Payback Period: 1-3 months**

### 3.2 Strategic Value

**Competitive Advantages:**

1. **Proactive Security Posture:** Early threat detection provides competitive advantage
2. **Customer Trust:** Enhanced security builds customer confidence
3. **Innovation Leadership:** Demonstrates commitment to cutting-edge security practices
4. **Scalability:** System can grow with business needs

**Risk Mitigation:**

- Reduced exposure to cyber threats
- Better compliance with security regulations (GDPR, SOC 2, ISO 27001)
- Protection of intellectual property and sensitive data
- Business continuity assurance

### 3.3 Prioritization Framework

**High Priority (Quick Wins):**

1. Feature engineering improvements (Low complexity, high impact)
2. Hyperparameter optimization (Medium complexity, medium-high impact)
3. Enhanced monitoring and observability (Medium complexity, high operational value)

**Medium Priority (Strategic Investments):**

1. Automated model retraining pipeline (High complexity, high long-term value)
2. Database integration for historical analysis (Medium complexity, medium impact)
3. Advanced dashboard features (Medium complexity, high user value)

**Low Priority (Future Enhancements):**

1. Microservices architecture (High complexity, scalability benefit)
2. Mobile application (Medium complexity, convenience feature)
3. SOAR integration (High complexity, advanced automation)

---

## 4. Project Plan: Scope, Key Deliverables, and Suggested Changes

### 4.1 Project Scope

**In-Scope:**

- Development and deployment of ML-based anomaly detection system
- Real-time API for prediction serving
- Interactive dashboard for security analysts
- Email alerting system
- Model training and evaluation framework
- Documentation and operational runbooks

**Out-of-Scope (Future Phases):**

- Automated response actions (account lockout, IP blocking)
- Integration with external SIEM systems
- Mobile application development
- Multi-tenant architecture
- Advanced threat intelligence integration

### 4.2 Key Deliverables

**Phase 1: Foundation (Completed)**

- ✅ Data preprocessing pipeline
- ✅ Three ML models (Isolation Forest, One-Class SVM, Autoencoder)
- ✅ Model evaluation and comparison
- ✅ Basic REST API (FastAPI)
- ✅ Streamlit dashboard
- ✅ Email alerting system

**Phase 2: Enhancement (Recommended)**

- 🔄 Feature engineering improvements
- 🔄 Hyperparameter optimization
- 🔄 Model ensemble implementation
- 🔄 Enhanced monitoring and logging
- 🔄 Database integration for historical data

**Phase 3: Advanced Features (Future)**

- ⏳ Automated model retraining pipeline
- ⏳ Advanced explainability features
- ⏳ SOAR integration
- ⏳ Performance optimization and scaling

### 4.3 Suggested Changes and Improvements

#### 4.3.1 Immediate Improvements (Next 1-2 Months)

**1. Feature Engineering Enhancement**

- **Action:** Add temporal and behavioral features
- **Deliverable:** Enhanced feature set with 15-20 features
- **Timeline:** 2-3 weeks
- **Resources:** 1 data scientist, 1 engineer

**2. Model Performance Optimization**

- **Action:** Systematic hyperparameter tuning
- **Deliverable:** Optimized models with 5-10% accuracy improvement
- **Timeline:** 3-4 weeks
- **Resources:** 1 data scientist

**3. Monitoring and Observability**

- **Action:** Implement comprehensive logging and metrics
- **Deliverable:** Dashboard with real-time performance metrics
- **Timeline:** 2-3 weeks
- **Resources:** 1 engineer

#### 4.3.2 Short-Term Improvements (3-6 Months)

**1. Database Integration**

- **Action:** Integrate time-series database for historical storage
- **Deliverable:** Persistent storage with query capabilities
- **Timeline:** 4-6 weeks
- **Resources:** 2 engineers

**2. Automated Retraining Pipeline**

- **Action:** Build CI/CD pipeline for model retraining
- **Deliverable:** Automated weekly/monthly retraining
- **Timeline:** 6-8 weeks
- **Resources:** 2 engineers, 1 data scientist

**3. Enhanced Dashboard Features**

- **Action:** Add real-time updates, advanced filtering, custom alerts
- **Deliverable:** Production-ready dashboard
- **Timeline:** 4-6 weeks
- **Resources:** 1 frontend engineer, 1 backend engineer

#### 4.3.3 Long-Term Improvements (6-12 Months)

**1. Advanced ML Models**

- **Action:** Implement LSTM/Transformer models for sequence analysis
- **Deliverable:** Next-generation anomaly detection models
- **Timeline:** 8-12 weeks
- **Resources:** 2 data scientists, 1 ML engineer

**2. SOAR Integration**

- **Action:** Integrate with security orchestration platform
- **Deliverable:** Automated response capabilities
- **Timeline:** 10-12 weeks
- **Resources:** 2 engineers, 1 security specialist

**3. Microservices Architecture**

- **Action:** Refactor to microservices for better scalability
- **Deliverable:** Scalable, distributed system
- **Timeline:** 12-16 weeks
- **Resources:** 3-4 engineers

### 4.4 Risk Management

**Technical Risks:**

- **Model Performance Degradation:** Mitigation through continuous monitoring and automated retraining
- **Scalability Issues:** Mitigation through load testing and architecture improvements
- **Data Quality Issues:** Mitigation through data validation and quality checks

**Operational Risks:**

- **Alert Fatigue:** Mitigation through intelligent threshold tuning and alert prioritization
- **System Downtime:** Mitigation through redundancy and failover mechanisms
- **Resource Constraints:** Mitigation through cloud auto-scaling

**Business Risks:**

- **Changing Requirements:** Mitigation through agile development and regular stakeholder communication
- **Budget Constraints:** Mitigation through phased approach and ROI demonstration
- **Competing Priorities:** Mitigation through clear business case and executive sponsorship

---

## 5. Project Tracking and Success Metrics

### 5.1 Key Performance Indicators (KPIs)

#### 5.1.1 Model Performance Metrics

**Primary Metrics:**

- **Accuracy:** Target >70% (Current: 59-63%)
- **Precision:** Target >75% (Current: 50-81%)
- **Recall:** Target >70% (Current: 10-59%)
- **F1-Score:** Target >72% (Current: 18-59%)
- **ROC-AUC:** Target >0.80 (Current: ~0.60)

**Measurement Frequency:** Weekly during development, monthly in production

#### 5.1.2 System Performance Metrics

**Operational Metrics:**

- **API Response Time:** Target <100ms (P95)
- **System Uptime:** Target >99.9%
- **Throughput:** Target >1,000 requests/second
- **Error Rate:** Target <0.1%

**Measurement Frequency:** Real-time monitoring with daily reports

#### 5.1.3 Business Impact Metrics

**Security Metrics:**

- **Mean Time to Detect (MTTD):** Target <5 minutes
- **Mean Time to Respond (MTTR):** Target <30 minutes
- **False Positive Rate:** Target <10%
- **True Positive Rate:** Target >85%

**Operational Efficiency:**

- **Investigation Time per Alert:** Target <15 minutes (Current: ~45 minutes)
- **Alerts Processed per Analyst:** Target >50/day
- **Automated Response Rate:** Target >60% of low-risk anomalies

**Measurement Frequency:** Weekly reports, monthly trend analysis

### 5.2 Tracking Methodology

**Data Collection:**

1. **Model Performance:** Automated evaluation on test sets and production data
2. **System Metrics:** Application Performance Monitoring (APM) tools
3. **Business Metrics:** Integration with ticketing and incident management systems
4. **User Feedback:** Regular surveys and interviews with security analysts

**Reporting:**

- **Daily:** System health and error rates
- **Weekly:** Model performance and business metrics
- **Monthly:** Comprehensive dashboard with trends and recommendations
- **Quarterly:** Executive summary with ROI analysis

### 5.3 Success Criteria

**Phase 1 Success Criteria (Completed):**

- ✅ Three ML models implemented and evaluated
- ✅ REST API operational with <200ms response time
- ✅ Dashboard functional with basic visualizations
- ✅ Email alerting system operational

**Phase 2 Success Criteria (Target):**

- 🎯 Model accuracy improved to >70%
- 🎯 False positive rate reduced to <10%
- 🎯 Automated retraining pipeline operational
- 🎯 Database integration complete

**Phase 3 Success Criteria (Future):**

- 🎯 MTTD reduced to <5 minutes
- 🎯 85%+ true positive rate
- 🎯 SOAR integration operational
- 🎯 System handles 10,000+ events/second

### 5.4 Continuous Improvement Process

**Feedback Loops:**

1. **Model Performance Monitoring:** Automated alerts on performance degradation
2. **User Feedback Collection:** Regular surveys and feature requests
3. **Security Incident Analysis:** Post-incident reviews to identify detection gaps
4. **Competitive Analysis:** Monitoring industry best practices and new techniques

**Iteration Cycle:**

- **Sprint Duration:** 2 weeks
- **Review Frequency:** End of each sprint
- **Retrospective:** Monthly team retrospectives
- **Model Retraining:** Weekly or monthly based on data volume

---

## 6. Summary of Project Outcome and Lessons Learned

### 6.1 Project Outcomes

#### 6.1.1 Technical Achievements

**Successfully Delivered:**

1. **Multi-Model Anomaly Detection System:** Three different ML approaches providing diverse detection capabilities
2. **Real-Time Prediction API:** FastAPI-based service with sub-second response times
3. **Interactive Dashboard:** Streamlit application enabling security analysts to investigate anomalies
4. **Automated Alerting:** Email notifications for critical anomalies with detailed context
5. **Explainability Features:** SHAP integration providing model interpretability

**Performance Results:**

- Isolation Forest: 59% accuracy, balanced precision/recall
- One-Class SVM: 59% accuracy, similar performance to Isolation Forest
- Autoencoder: 63% accuracy but low anomaly recall (10%)
- Overall system capable of processing real-time authentication events

#### 6.1.2 Business Value Delivered

**Immediate Benefits:**

- Automated anomaly detection reducing manual monitoring effort
- Real-time threat detection capabilities
- Improved visibility into authentication patterns
- Foundation for advanced security analytics

**Strategic Value:**

- Zero-trust security architecture implementation
- Scalable platform for future enhancements
- Data-driven security decision making
- Enhanced security posture

### 6.2 Key Lessons Learned

#### 6.2.1 Technical Lessons

**1. Model Selection and Evaluation**

- **Lesson:** Different models excel at different anomaly types
- **Insight:** Ensemble approaches may provide better overall performance
- **Application:** Consider model stacking or voting for production

**2. Feature Engineering Importance**

- **Lesson:** Simple features (hour, bytes_transferred) are highly effective
- **Insight:** Temporal and behavioral features significantly improve detection
- **Application:** Invest in feature engineering before complex model architectures

**3. Explainability is Critical**

- **Lesson:** Security teams need to understand why an event is flagged
- **Insight:** SHAP values provide actionable insights for investigations
- **Application:** Prioritize explainability features in production systems

**4. Real-Time Processing Challenges**

- **Lesson:** Categorical encoding for new values requires careful handling
- **Insight:** Preprocessing pipeline must handle unseen categories gracefully
- **Application:** Implement robust data validation and fallback mechanisms

#### 6.2.2 Process Lessons

**1. Iterative Development Approach**

- **Lesson:** Starting with multiple models provided valuable comparisons
- **Insight:** Rapid prototyping enabled quick learning and iteration
- **Application:** Continue agile approach with regular model updates

**2. User-Centric Design**

- **Lesson:** Dashboard usability directly impacts analyst productivity
- **Insight:** Security analysts need fast access to relevant information
- **Application:** Regular user feedback sessions essential for UX improvements

**3. Operational Considerations**

- **Lesson:** Email alerting requires careful configuration and testing
- **Insight:** Alert fatigue is a real concern with high false positive rates
- **Application:** Implement intelligent alert prioritization and threshold tuning

**4. Documentation and Maintenance**

- **Lesson:** Well-documented code and processes enable faster onboarding
- **Insight:** Model retraining procedures need to be clearly documented
- **Application:** Maintain comprehensive documentation and runbooks

#### 6.2.3 Business Lessons

**1. ROI Demonstration**

- **Lesson:** Quantifiable metrics are essential for stakeholder buy-in
- **Insight:** Early wins (automated detection) provide immediate value
- **Application:** Track and report business metrics regularly

**2. Phased Approach**

- **Lesson:** Starting with MVP and iterating is more effective than big-bang delivery
- **Insight:** Each phase delivers incremental value
- **Application:** Continue phased enhancement approach

**3. Integration Challenges**

- **Lesson:** Kafka integration optionality added complexity
- **Insight:** External dependencies should be clearly defined and tested
- **Application:** Minimize optional dependencies or provide clear alternatives

### 6.3 Challenges Encountered

**Technical Challenges:**

1. **Low Anomaly Recall in Autoencoder:** Model struggled to identify anomalies despite good overall accuracy
   - **Resolution:** Focused on Isolation Forest for production, continued Autoencoder research
2. **Categorical Encoding for New Values:** Handling unseen categories in real-time predictions
   - **Resolution:** Implemented dynamic encoding with fallback mechanisms
3. **Model Performance Optimization:** Balancing precision and recall
   - **Resolution:** Used F1-score as primary metric, tuned contamination rates

**Operational Challenges:**

1. **Email Configuration Complexity:** Gmail App Password setup required multiple iterations
   - **Resolution:** Created detailed documentation and setup guides
2. **Dashboard Performance:** Large datasets caused slow rendering
   - **Resolution:** Implemented filtering and pagination
3. **Real-Time Data Synchronization:** Ensuring dashboard reflects latest events
   - **Resolution:** File-based approach with manual refresh (future: real-time streaming)

### 6.4 Recommendations for Future Work

**Immediate Priorities (Next Quarter):**

1. **Feature Engineering:** Add temporal and behavioral features to improve model accuracy
2. **Hyperparameter Optimization:** Systematic tuning to achieve >70% accuracy
3. **Monitoring Enhancement:** Comprehensive observability for production operations

**Short-Term Priorities (6 Months):**

1. **Automated Retraining:** Implement CI/CD pipeline for model updates
2. **Database Integration:** Historical storage and analysis capabilities
3. **Advanced Dashboard:** Real-time updates and enhanced filtering

**Long-Term Vision (12+ Months):**

1. **Advanced ML Models:** LSTM/Transformer for sequence analysis
2. **SOAR Integration:** Automated response and orchestration
3. **Enterprise Scalability:** Microservices architecture for high-volume deployments

### 6.5 Conclusion

The Zero-Trust Anomaly Detection System project successfully delivered a functional ML-based security monitoring solution. While model performance (59-63% accuracy) has room for improvement, the system provides a solid foundation for real-time anomaly detection with clear paths for enhancement.

The project demonstrated the value of:

- **Iterative Development:** Rapid prototyping and continuous improvement
- **Multi-Model Approach:** Diversity in detection methods
- **Explainability:** SHAP integration for actionable insights
- **User-Centric Design:** Dashboard and alerting tailored to security analysts

**Key Success Factors:**

- Clear problem definition and requirements
- Agile development methodology
- Focus on operational usability
- Comprehensive documentation

**Next Steps:**

1. Implement Phase 2 improvements (feature engineering, optimization)
2. Deploy to production with monitoring
3. Gather user feedback and iterate
4. Plan Phase 3 advanced features

The project has established a strong foundation for zero-trust security monitoring, with clear opportunities for enhancement and significant potential for business value through improved threat detection and operational efficiency.

---

## Appendices

### Appendix A: Technical Architecture

**Components:**

- **Model Training:** Jupyter notebook with scikit-learn and TensorFlow
- **API Service:** FastAPI with joblib model loading
- **Dashboard:** Streamlit with Plotly visualizations
- **Alerting:** SMTP email integration
- **Streaming:** Optional Kafka integration

**Technology Stack:**

- Python 3.11+
- scikit-learn, TensorFlow, pandas, numpy
- FastAPI, Streamlit
- Kafka (optional), Docker

### Appendix B: Model Performance Summary

| Model            | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| ---------------- | -------- | --------- | ------ | -------- | ------- |
| Isolation Forest | 59%      | 50-68%    | 59%    | 54-63%   | ~0.60   |
| One-Class SVM    | 59%      | 50-68%    | 59%    | 54-59%   | ~0.60   |
| Autoencoder      | 63%      | 62-81%    | 10-98% | 18-76%   | ~0.54   |

### Appendix C: Project Timeline

**Phase 1 (Completed):** 8-10 weeks

- Weeks 1-2: Data exploration and preprocessing
- Weeks 3-5: Model development and evaluation
- Weeks 6-7: API and dashboard development
- Weeks 8-10: Integration, testing, and documentation

**Phase 2 (Planned):** 12-16 weeks

- Feature engineering and optimization
- Database integration
- Enhanced monitoring
- Automated retraining pipeline

---

**Document End**
