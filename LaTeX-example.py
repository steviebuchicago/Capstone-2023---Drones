import matplotlib.pyplot as plt
from tabulate import tabulate

# Sample data
students = [
    ["Alice", 85],
    ["Bob", 78],
    ["Charlie", 92],
    ["David", 89]
]

# Generate a plot
names = [student[0] for student in students]
scores = [student[1] for student in students]

plt.figure(figsize=(8,6))
plt.bar(names, scores, color=['red', 'green', 'blue', 'cyan'])
plt.xlabel('Student Name')
plt.ylabel('Score')
plt.title('Student Scores')
plt.savefig('scores_plot.png')

# Convert data to LaTeX table format
latex_table = tabulate(students, headers=['Name', 'Score'], tablefmt='latex')

# Create LaTeX document
latex_document = r"""
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\section{Student Scores}

% Inserting the table
%s

% Inserting the plot
\begin{figure}[h!]
    \centering
    \includegraphics[width=0.8\textwidth]{scores_plot.png}
    \caption{Bar chart of student scores.}
\end{figure}

\end{document}
""" % latex_table

with open("report.tex", "w") as f:
    f.write(latex_document)
