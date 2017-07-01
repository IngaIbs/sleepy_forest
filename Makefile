HOST?=ddpg
SIZE?=64

%.pdf:
	cd slides && \
	pandoc \
		-t beamer \
		--latex-engine=pdflatex \
		--bibliography=library.bib \
		--csl=apa.csl \
		--highlight-style tango \
		--slide-level=2 \
		-o slides.pdf \
		slides.yaml *.md

# --listings


slides: slides/slides.pdf