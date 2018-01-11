FROM ubuntu

MAINTAINER Rémi Laurent

RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends install -y \
		python3-flask python3-pip && \
	apt-get clean all && \
	pip3 install statsmodels

RUN mkdir /app
COPY app.py football_analysis.py /app/
COPY static /app/static
COPY templates /app/templates

EXPOSE 5000
WORKDIR /app
ENTRYPOINT [ "/app/app.py" ]
