FROM debian:12

RUN apt-get update && apt-get install -y python3.11 python3.11-dev python3.11-venv python3-pip curl && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

RUN curl --location https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_S.gguf?download=true -o Meta-Llama-3-8B-Instruct.Q4_K_S.gguf

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV=/venv

COPY requirements.txt .
RUN pip install -r requirements.txt 

COPY . .

EXPOSE 5000
ENV LOCAL_LLM=1
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "-k", "gevent", "--worker-tmp-dir", "/dev/shm", "--timeout", "120", "ranking_server:app"]
