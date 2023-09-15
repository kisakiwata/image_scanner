FROM python:3.9.1

WORKDIR /models/research

# Expose port you want your app on
EXPOSE 8501

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

# Set PYTHONPATH
ENV PYTHONPATH=/models/research:$PYTHONPATH

# Copy app code and set working directory
COPY . .
WORKDIR /models/research


ENTRYPOINT ["streamlit", "run", "streamlit_dash.py", "--server.port=8501", "--server.address=0.0.0.0"]