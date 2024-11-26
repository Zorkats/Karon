# Karon: Research Assistant Tool

# 📖 Introduction

Karon is a tool designed for **researchers** to streamline their workflow when managing and organizing academic papers. It provides an intuitive and powerful interface to automate tasks like downloading papers, making queries for Scopus and Web of Science, among other features.

# ✨ Features

- **Automated Downloading**: Fetch academic papers directly from platforms like ScienceDirect, Nature, MDPI, Springer, among others. (This program can also fetch from Sci-hub, but it's an optional feature.)
- **Query Builder**: Create Queries for Scopus and Web of Science based on information you have like the Authors, Keywords, Date Range, and more. You can then download the data and you will have a .csv file with the DOIs already built!
- **Query Optimizer**: Grab two .csv files from Scopus and Web of Science, and fuse them so you won't download the same paper two times, or papers that you don't need.
- **User-Friendly Interface**: Designed for researchers of all expertise levels, alongside Themes to make it easier on the eyes.
- **API Support**: If you have an API for one of the paper publishers, you can use that to download your paper without any problems!

  Currently, the supported APIs are:
- Elsevier (along with it's Institutional Token, in case you have one)
- Web of Science
- IEEE
- Springer

If you have an API you would like me to implement, leave an issue and I will work on it!

# 🛠️ How to Install

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your_user/karon.git
   cd karon

2. **Install the dependencies**:[requirements.txt](https://github.com/user-attachments/files/17925026/requirements.txt)
   ```bash
   pip install -r requirements.txt


3. **Set up Playwright**:
   This is necessary to run Playwright with it's default browsers, in the case you don't want to install Ungoogled Chromium.
   ```bash
   pip install playwright

5. **Run the Application**:
   ```bash
   python main.py

# 🚀 How to Use

1. Open Karon by running `main.py`..
2. Use the tabs to access the available tools:
   - **Download Papers**
   - **Query Builder**
   - **Query Optimizer**
   - **WordCloud**
   - **Statistics**


# 👨‍💻 Contributions

Contributions are welcome! If you have ideas, suggestions, feature requests or encounter an issue, please feel free to leave an issue, I swear I will look at it eventually.

# 🔧 TODO
-Implement multi-language support.

-Add more identifiers beside DOIs. (Like PMID)

-Implement the Statistics Tab on it's full capacity, including a Deep Learning model to resume the papers you downloaded.

-Implement an executable file for people that does not want to install Python and the dependencies.

-More to come!


# 🌟FAQ
 **¿Why did you make this program?**
 
 This program was born after I was tasked on an investigation on my university to make a webscrapper to download multiple papers, for the purpose of doing an SLR. The thing that I noticed, is that a lot of tools and webscrappers were either outdated, behind a paywall, or they simply didn't work. So after I made the initial version for the investigation, I kept working on it to make it a fully made program with GUI and features, so people would find it and use it without having a lot of problems.
 
 **¿Why the name Karon?**
 
 This is funny because, while I was developing this, I was playing ASTLIBRA Revision, a very good JRPG which has probably became one of my favorite games ever made. I would spent a whole hour writing about it, but the thing is one of the protagonists (which is a talking crow, hence the logo) is named Karon. And considering Sci-hub's logo is also a crow, I thought it was fitting.

# 🛡️ License

Karon is licensed under the **GNU General Public License version 3**. See the `LICENSE` file for more details.

# 📫 Contact

Have questions or suggestions? Feel free to reach out:

- **Email**: [email@example.com](vicentemediano1@gmail.com)
- **GitHub Issues**: [Open an Issue](https://github.com/Zorkats/karon/issues)




