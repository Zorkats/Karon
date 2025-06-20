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

2. **Install the dependencies**: [requirements.txt](https://github.com/user-attachments/files/17925026/requirements.txt)
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

# 🖥️ Command-Line Usage

Karon can also be used via the command line without the GUI. The following options are supported when running python main.py:
--help: Show available command-line options and usage.
--version: Print the current version of Karon and exit.
--download <DOI>: Download the paper for the given DOI and save it to the downloads folder (without launching the GUI).
--gui: Force launch the GUI (this is the default behavior if no flag is provided).

When using CLI download, Karon will ensure the required browser is installed and then download the PDF for the specified DOI using available APIs or web scraping (and Sci-Hub as a fallback if enabled in the config). A config.json file is automatically created on first run with default settings (API keys, preferences, etc.), and all actions are logged to logs/karon.log.


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
 
 This program was born after I was tasked on an investigation on my university to make a web scraper to download multiple papers, for the purpose of doing an SLR. The thing that I noticed, is that a lot of tools and webscrappers were either outdated, behind a paywall, or they simply didn't work. So after I made the initial version for the investigation, I kept working on it to make it a fully made program with GUI and features, so people would find it and use it without having a lot of problems.
 
 **¿Why the name Karon?**
 
 This is funny because, while I was developing this, I was playing ASTLIBRA Revision, a very good JRPG which has probably become one of my favorite games ever made. I could spent a whole hour writing about it, but the thing is one of the protagonists (which is a talking crow, hence the logo) is named Karon. Given that Sci-Hub's logo is also a crow, the name felt fitting for a research assistant tool!

# 🛡️ License

Karon is licensed under the **GNU General Public License version 3**. See the `LICENSE` file for more details.

# 📫 Contact and Donations

If you have a question or you want to make a donation (I would really really really love you) feel free to message me and leave a donation through the Sponsor button or the Paypal link below.

- **Email**: [vicentemediano1@gmail.com](vicentemediano1@gmail.com)
- **GitHub Issues**: [Open an Issue](https://github.com/Zorkats/karon/issues)
- **Donate through PayPal**: [Here](https://www.paypal.com/donate/?hosted_button_id=C8JD8HGFTEJB2)




