FROM continuumio/miniconda3:4.10.3

WORKDIR /app

COPY environment.yml .
RUN conda env create -f environment.yml

COPY requirements.txt requirements.txt
RUN /bin/bash -c "source activate ldm && pip install -r requirements.txt"

COPY . .

CMD [ "/bin/bash", "-c", "source activate ldm && python comic_generator.py" ]
