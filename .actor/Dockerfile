# FROM apify/actor-python:3.13

# # Install dependencies for Chrome
# RUN apt-get update && apt-get install -y \
#     wget \
#     unzip \
#     gnupg \
#     ca-certificates \
#     fonts-liberation \
#     libappindicator3-1 \
#     libasound2 \
#     libatk-bridge2.0-0 \
#     libatk1.0-0 \
#     libcups2 \
#     libdbus-1-3 \
#     libdrm2 \
#     libgbm1 \
#     libgtk-3-0 \
#     libnspr4 \
#     libnss3 \
#     libx11-xcb1 \
#     libxcomposite1 \
#     libxdamage1 \
#     libxrandr2 \
#     libxss1 \
#     libxtst6 \
#     xdg-utils

# # Install Chrome stable
# RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update && apt-get install -y google-chrome-stable

# COPY requirements.txt ./

# RUN pip install -r requirements.txt

# COPY . ./

# RUN python3 -m compileall -q src/

# RUN useradd --create-home apify && chown -R apify:apify ./
# USER apify

# CMD ["python3", "-m", "src"]





# IMPORTANT: Use Python 3.12, NOT 3.13
FROM apify/actor-python:3.12

# Install Chrome dependencies first
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run the actor
CMD ["python", "-m", "src"]