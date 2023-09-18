FROM python:3.9.1


# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox


WORKDIR /models/research

# Set PYTHONPATH
#ENV PYTHONPATH=/models/research:$PYTHONPATH

# Install Chrome and Chrome WebDriver using apt-get
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver


# Expose port you want your app on
EXPOSE 8501

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt


# Copy app code and set working directory
COPY . .
WORKDIR /models/research


ENTRYPOINT ["streamlit", "run", "streamlit_dash.py", "--server.port=8501", "--server.address=0.0.0.0"]