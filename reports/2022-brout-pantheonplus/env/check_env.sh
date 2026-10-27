#!/bin/bash
source /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/env/activate.sh
python -c "import numpy, scipy, pandas, emcee, dynesty, camb; print(numpy.__version__, scipy.__version__, pandas.__version__, emcee.__version__, dynesty.__version__, camb.__version__)" 2>&1
echo "exit $?"
