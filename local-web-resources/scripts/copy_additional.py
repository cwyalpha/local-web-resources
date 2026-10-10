#!/usr/bin/env python3
"""Copy the additional library subset using the shared exact-version lock."""
from copy_resources import main

if __name__=='__main__':
    main({'katex','reveal.js','cropperjs','fuse.js','cytoscape','jstree','markdown-it',
          'echarts-stat','wordcloud2','impress.js'})
