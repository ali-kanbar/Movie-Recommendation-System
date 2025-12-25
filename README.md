# 🎬 NLP Movie Recommendation System: TF-IDF vs. BERT

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit--Learn-orange)
![Transformers](https://img.shields.io/badge/Library-HuggingFace-yellow)
![Status](https://img.shields.io/badge/Status-Complete-green)

## 📌 Project Overview
This project builds and compares two different Natural Language Processing (NLP) approaches to recommend movies based on viewing history. The system analyzes movie titles and grouped themes to predict which movies a user is most likely to watch next.

The core experiment compares **Traditional Keyword Matching (TF-IDF)** against **Contextual Deep Learning (BERT)** to determine which is more effective for short-text title recommendation.

## 📊 The Experiment & Results

We trained two distinct models on a dataset of 50 thematic movie groups (ranging from *Alien Invasions* to *Courtroom Dramas*).

### 1. TF-IDF (The Winner 🏆)
* **Approach:** Uses statistical weighting to find exact keyword matches (e.g., linking "Iron Man" to "Iron Man 2").
* **Performance:**
    * **AUC:** 0.97 (Outstanding distinction between liked/disliked items)
    * **Recall@20:** 95.8% (Found almost all relevant movies)
    * **MAP:** 0.86

### 2. BERT (The Challenger)
* **Approach:** Uses transformer-based embeddings to find semantic similarities.
* **Performance:**
    * **AUC:** 0.88
    * **Recall@20:** 79.5%

### 💡 Key Insight
**Why did the simpler model win?**
Movie titles function more like **labels** than sentences. TF-IDF excelled because it created strong, direct links between specific tokens (like "Harry Potter" or "Matrix"), whereas BERT attempted to find semantic nuance where direct keyword matching was actually preferred.

---

## 📂 Dataset Groups
The dataset consists of 50 distinct thematic clusters, including:
* **Group 1:** Alien Invasions (e.g., *Alien*, *Arrival*)
* **Group 5:** Superheroes (e.g., *Avengers*, *The Dark Knight*)
* **Group 13:** Heists (e.g., *Ocean's Eleven*, *Inception*)
* **Group 38:** Time Loops (e.g., *Groundhog Day*, *Happy Death Day*)
* ...and 46 others.

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/your-username/movie-recommendation-system.git](https://github.com/your-username/movie-recommendation-system.git)
   cd movie-recommendation-system

```

2. **Install dependencies**
```bash
pip install pandas scikit-learn transformers torch huggingface_hub joblib matplotlib

```


3. **Environment Variables (Optional)**
If you plan to retrain or upload models, rename `.env.example` to `.env` and add your keys.
* ⚠️ **Note:** Never upload your actual `.env` file to GitHub!



---

## 🚀 Usage

### Running the Notebook

The core logic is contained within `Movie_Recommendation_System.ipynb`.

```bash
jupyter notebook Movie_Recommendation_System.ipynb

```

### Loading the Model (from Hugging Face)

You can load the pre-trained TF-IDF model directly from the Hub:

```python
from huggingface_hub import hf_hub_download
import joblib

# Download model files
vectorizer_path = hf_hub_download(repo_id="your-username/movie-recommender-tfidf", filename="tfidf_vectorizer.joblib")
matrix_path = hf_hub_download(repo_id="your-username/movie-recommender-tfidf", filename="tfidf_matrix.joblib")

# Load models
tfidf_vectorizer = joblib.load(vectorizer_path)
tfidf_matrix = joblib.load(matrix_path)

print("Model loaded successfully!")

```

---

## 🔗 Model Links

The trained models are hosted on Hugging Face for easy access:

* **TF-IDF Model (Best Performance):** [Link to your HF Repo]
* **BERT Model (Experimental):** [Link to your HF Repo]

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

[MIT](https://choosealicense.com/licenses/mit/)

```

### Next Step for you:
1. Create the `README.md` file in your folder.
2. Paste the text above.
3. **Important:** Replace `your-username/movie-recommender-tfidf` and `[Link to your HF Repo]` with your actual Hugging Face username and repository links once you upload them!
