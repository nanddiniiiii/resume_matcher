"""
Add diverse sample jobs to the database.
Creates 50+ jobs across different tech categories.
"""
from app.database import SessionLocal
from app.models.job import Job
from app.services.job_matcher import JobMatcher


def add_sample_jobs():
    db = SessionLocal()

    # Simpler format matching Job model: title, company, description, required_skills, location, job_type
    jobs_data = []

    # Frontend (10)
    frontend_jobs = [
        ("Senior React Developer", "TechCorp", "Build modern web apps with React, TypeScript, and Next.js. 5+ years experience required.", ["React", "TypeScript", "Next.js", "Redux"], "Remote", "remote"),
        ("Vue.js Engineer", "StartupHub", "Create SaaS applications with Vue.js 3. 3+ years Vue experience needed.", ["Vue.js", "JavaScript", "Vuex", "HTML", "CSS"], "Austin, TX", "hybrid"),
        ("UI/UX Developer", "Design Systems", "Build accessible interfaces. Strong CSS and JavaScript skills required.", ["HTML", "CSS", "JavaScript", "React", "Figma"], "New York, NY", "onsite"),
        ("Angular Developer", "Enterprise Solutions", "Enterprise Angular apps. 4+ years Angular, TypeScript, RxJS.", ["Angular", "TypeScript", "RxJS", "NgRx"], "Seattle, WA", "remote"),
        ("Full Stack JS Developer", "WebApps Pro", "Node.js and React full stack. MongoDB and REST API experience.", ["React", "Node.js", "MongoDB", "Express", "JavaScript"], "Boston, MA", "hybrid"),
        ("Mobile Web Developer", "MobileTech", "Responsive mobile-first applications. PWA and performance optimization.", ["HTML", "CSS", "JavaScript", "PWA", "React"], "Los Angeles, CA", "remote"),
        ("Frontend Performance Engineer", "SpeedTech", "Optimize web performance. Webpack, Lighthouse, WebVitals expertise.", ["JavaScript", "Webpack", "Performance", "React"], "Denver, CO", "remote"),
        ("Svelte Developer", "Modern Web", "High-performance Svelte and SvelteKit applications.", ["Svelte", "JavaScript", "SvelteKit", "HTML", "CSS"], "Portland, OR", "hybrid"),
        ("Accessibility Specialist", "Inclusive Tech", "WCAG compliance and accessibility audits. Screen reader testing.", ["Accessibility", "HTML", "JavaScript", "ARIA", "WCAG"], "Chicago, IL", "remote"),
        ("Frontend Architect", "Enterprise Web", "Lead frontend architecture. 8+ years experience, leadership skills.", ["React", "TypeScript", "Architecture", "Leadership"], "San Jose, CA", "hybrid"),
    ]

    # Backend (10)
    backend_jobs = [
        ("Senior Python Engineer", "DataFlow", "FastAPI microservices with PostgreSQL. 5+ years Python experience.", ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"], "Remote", "remote"),
        ("Node.js Developer", "CloudNative", "Build high-performance APIs with Node.js, Express, MongoDB.", ["Node.js", "Express", "MongoDB", "JavaScript", "AWS"], "Miami, FL", "remote"),
        ("Java Spring Boot Developer", "Enterprise Java", "Enterprise Spring Boot applications. Kafka and Hibernate.", ["Java", "Spring Boot", "Hibernate", "PostgreSQL", "Kafka"], "Dallas, TX", "hybrid"),
        ("Go Backend Engineer", "HighPerf Systems", "Microservices in Go. gRPC and Kubernetes experience.", ["Go", "gRPC", "Kubernetes", "Docker", "PostgreSQL"], "San Francisco, CA", "remote"),
        ("Ruby on Rails Developer", "WebRails", "Rails applications with PostgreSQL and Redis.", ["Ruby", "Rails", "PostgreSQL", "Redis", "Sidekiq"], "Portland, OR", "hybrid"),
        ("PHP Laravel Developer", "Modern PHP", "Laravel APIs and integrations. MySQL and Docker.", ["PHP", "Laravel", "MySQL", "REST API", "Docker"], "Atlanta, GA", "remote"),
        (".NET Core Developer", "Microsoft Solutions", ".NET Core with C# and Azure cloud services.", ["C#", ".NET Core", "SQL Server", "Azure", "REST API"], "Redmond, WA", "hybrid"),
        ("API Platform Engineer", "API Gateway", "API gateways with Kong and OAuth2. Security focus.", ["REST API", "GraphQL", "OAuth", "Kong", "Kubernetes"], "Seattle, WA", "remote"),
        ("Database Engineer", "Data Systems", "PostgreSQL and MySQL optimization. Replication and backup.", ["PostgreSQL", "MySQL", "SQL", "Redis", "MongoDB"], "Austin, TX", "hybrid"),
        ("GraphQL Developer", "Modern APIs", "GraphQL APIs with Node.js. Apollo Server and schema design.", ["GraphQL", "Node.js", "Apollo", "TypeScript", "PostgreSQL"], "Boston, MA", "remote"),
    ]

    # Data Science (10)
    ds_jobs = [
        ("Machine Learning Engineer", "AI Innovations", "ML models with PyTorch/TensorFlow. MLOps and AWS SageMaker.", ["Python", "Machine Learning", "PyTorch", "TensorFlow", "AWS"], "San Francisco, CA", "hybrid"),
        ("Data Scientist", "Analytics Pro", "Statistical modeling and predictive analytics. Python, R, SQL.", ["Python", "R", "SQL", "Machine Learning", "Statistics"], "New York, NY", "hybrid"),
        ("NLP Engineer", "Language AI", "Natural language processing with transformers and BERT.", ["Python", "NLP", "PyTorch", "Transformers", "BERT"], "Remote", "remote"),
        ("Computer Vision Engineer", "Visual AI", "Object detection and image classification. OpenCV and CNNs.", ["Python", "Computer Vision", "OpenCV", "PyTorch", "Deep Learning"], "Seattle, WA", "hybrid"),
        ("MLOps Engineer", "ML Platform", "ML infrastructure with Kubeflow and MLflow. Model monitoring.", ["Python", "MLOps", "Kubernetes", "Docker", "MLflow"], "San Jose, CA", "remote"),
        ("Data Engineer", "Big Data Systems", "Data pipelines with Spark and Airflow. ETL processes.", ["Python", "Spark", "Airflow", "SQL", "ETL"], "Chicago, IL", "hybrid"),
        ("AI Research Scientist", "Deep Learning Lab", "Cutting-edge AI research. PhD required, publication record.", ["Python", "Deep Learning", "Research", "PyTorch", "TensorFlow"], "Stanford, CA", "onsite"),
        ("Analytics Engineer", "Business Intelligence", "Data modeling with dbt and SQL. BI tools expertise.", ["SQL", "dbt", "Python", "Data Modeling", "Tableau"], "Austin, TX", "remote"),
        ("Recommendation Engineer", "Personalization Tech", "Recommendation engines with collaborative filtering and ML.", ["Python", "Machine Learning", "TensorFlow", "Spark", "SQL"], "San Francisco, CA", "hybrid"),
        ("Time Series Analyst", "Forecasting Solutions", "Forecasting models. ARIMA, Prophet, deep learning.", ["Python", "R", "Time Series", "Statistics", "Prophet"], "New York, NY", "remote"),
    ]

    # DevOps (10)
    devops_jobs = [
        ("Senior DevOps Engineer", "Cloud Infrastructure", "AWS, Terraform, Kubernetes. 5+ years DevOps experience.", ["DevOps", "AWS", "Kubernetes", "Terraform", "Docker"], "Seattle, WA", "remote"),
        ("Site Reliability Engineer", "High Availability", "System reliability with Prometheus and Grafana. On-call rotation.", ["SRE", "Kubernetes", "Prometheus", "Grafana", "Python"], "San Francisco, CA", "hybrid"),
        ("Cloud Architect", "Enterprise Cloud", "Multi-cloud architecture. AWS/Azure certifications required.", ["AWS", "Azure", "Cloud Architecture", "Terraform", "Kubernetes"], "New York, NY", "hybrid"),
        ("Kubernetes Engineer", "Container Orchestration", "K8s clusters and GitOps. Helm and ArgoCD.", ["Kubernetes", "Docker", "Helm", "GitOps", "AWS"], "Austin, TX", "remote"),
        ("IaC Engineer", "Automation Systems", "Infrastructure as Code with Terraform and Ansible.", ["Terraform", "Ansible", "AWS", "Azure", "Python"], "Denver, CO", "remote"),
        ("CI/CD Engineer", "Build Pipeline", "Jenkins, GitLab CI, GitHub Actions. Pipeline optimization.", ["CI/CD", "Jenkins", "Docker", "Kubernetes", "Git"], "Boston, MA", "hybrid"),
        ("Cloud Security Engineer", "SecureCloud", "Cloud security and compliance. SOC2 and HIPAA.", ["Cloud Security", "AWS", "Azure", "IAM", "Terraform"], "Washington, DC", "hybrid"),
        ("Platform Engineer", "Developer Platform", "Internal developer platforms. Improve developer experience.", ["Kubernetes", "Docker", "Python", "Go", "API Design"], "San Francisco, CA", "remote"),
        ("Observability Engineer", "Telemetry Systems", "Monitoring with Prometheus, Grafana, ELK stack.", ["Prometheus", "Grafana", "ELK", "Monitoring", "Kubernetes"], "Chicago, IL", "remote"),
        ("Network Engineer", "Network Infrastructure", "VPNs, load balancers, firewalls. Cloud networking.", ["Networking", "AWS", "VPN", "Load Balancing", "Linux"], "Dallas, TX", "hybrid"),
    ]

    # Mobile (5)
    mobile_jobs = [
        ("iOS Developer", "Mobile Apps Studio", "Native iOS with Swift and SwiftUI. App Store publishing.", ["iOS", "Swift", "SwiftUI", "UIKit", "Xcode"], "Los Angeles, CA", "hybrid"),
        ("Android Developer", "Android Innovations", "Kotlin and Jetpack Compose. MVVM architecture.", ["Android", "Kotlin", "Jetpack Compose", "MVVM", "Room"], "San Diego, CA", "hybrid"),
        ("React Native Developer", "Cross-Platform Mobile", "Cross-platform apps with React Native.", ["React Native", "JavaScript", "TypeScript", "Redux"], "Miami, FL", "remote"),
        ("Flutter Developer", "Dart Mobile", "Beautiful Flutter applications. Custom widgets and animations.", ["Flutter", "Dart", "Mobile Development", "Firebase"], "Austin, TX", "remote"),
        ("Mobile DevOps Engineer", "Mobile CI/CD", "Mobile pipelines with Fastlane. iOS/Android builds.", ["Mobile DevOps", "Fastlane", "CI/CD", "iOS", "Android"], "Seattle, WA", "remote"),
    ]

    # Security (5)
    security_jobs = [
        ("Security Engineer", "CyberSec", "Penetration testing and security audits. OWASP expertise.", ["Security", "Penetration Testing", "OWASP", "Python", "Linux"], "Washington, DC", "hybrid"),
        ("Application Security Engineer", "AppSec Pro", "Code reviews and SAST/DAST. Secure coding practices.", ["Application Security", "SAST", "DAST", "Threat Modeling", "Python"], "San Francisco, CA", "remote"),
        ("Incident Response Engineer", "SOC Operations", "Security incidents and forensics. 24/7 SOC environment.", ["Incident Response", "SIEM", "Forensics", "Threat Hunting", "Security"], "New York, NY", "hybrid"),
        ("IAM Engineer", "IAM Solutions", "Okta, Active Directory, SSO, and MFA systems.", ["IAM", "Okta", "SAML", "OAuth", "Active Directory"], "Boston, MA", "remote"),
        ("Compliance Engineer", "Regulatory Tech", "SOC2, HIPAA, GDPR compliance programs.", ["Compliance", "SOC2", "HIPAA", "GDPR", "Auditing"], "Chicago, IL", "hybrid"),
    ]

    # Combine all jobs
    all_job_tuples = frontend_jobs + backend_jobs + ds_jobs + devops_jobs + mobile_jobs + security_jobs

    for title, company, description, skills, location, job_type in all_job_tuples:
        jobs_data.append({
            "title": title,
            "company": company,
            "description": description,
            "required_skills": skills,
            "location": location,
            "job_type": job_type
        })

    print(f"Adding {len(jobs_data)} jobs to database...")

    try:
        matcher = JobMatcher()
        added = 0
        for job_data in jobs_data:
            if db.query(Job).filter(Job.title == job_data['title'], Job.company == job_data['company']).first():
                continue
            embedding = matcher.generate_embedding(matcher.prepare_job_text(job_data))
            db.add(Job(**job_data, embedding=embedding, source="sample"))
            added += 1
        db.commit()
        print(f"Added {added} sample jobs with embeddings")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_jobs()
