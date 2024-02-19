## To change UCR Taint checker version for annotator, change version in annotator.py script

ANNOTATOR_TYPE_ARG=true ANNOTATOR_POLY=true ANNOTATOR_LIBRARY=true UCRT_VERSION=0.1-alpha-2 ./gradlew core:compileJava --rerun-tasks
