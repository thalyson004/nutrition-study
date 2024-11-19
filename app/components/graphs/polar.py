import numpy as np
import matplotlib.pyplot as plt


def plot_multiple_polar_charts(data_list, num_points=36, labels=None, save_path=None):
    """
    Gera múltiplos gráficos polares em uma única imagem, com opção de salvar a imagem e personalizar labels.

    Parameters:
    - data_list (list of dict): Lista de dicionários com dados para cada gráfico.
      Cada dicionário deve ter as chaves:
      - "variable_name" (str): Nome da variável.
      - "x_data" (list or np.array): Dados para mulheres.
      - "y_data" (list or np.array): Dados para homens.
      - "x_label" (str): Descrição do intervalo para mulheres.
      - "y_label" (str): Descrição do intervalo para homens.
    - num_points (int): Número de pontos em cada gráfico. Padrão é 36.
    - labels (list of str, optional): Labels ao redor do círculo. Deve ter o mesmo comprimento que `num_points`.
                                      Se None, os números em graus serão usados como labels.
    - save_path (str, optional): Caminho completo para salvar a imagem gerada.
                                 Se None, a imagem será exibida.

    Exemplo de Uso:
    plot_multiple_polar_charts([{"variable_name": "Energy",
                                 "x_data": x_energy_data,
                                 "y_data": final_energy_data,
                                 "x_label": "1600 kcal - 2200 kcal",
                                 "y_label": "2400 kcal - 3000 kcal"}],
                                labels=["A", "B", "C", ...],
                                save_path="output.png")
    """
    if labels and len(labels) != num_points:
        raise ValueError(
            "O número de labels deve ser igual ao número de pontos (num_points)."
        )

    if labels:
        labels.append(labels[0])

    num_charts = len(data_list)

    # Ajuste para layout em uma linha se houver exatamente dois gráficos
    if num_charts == 2:
        rows, cols = 1, 2
    else:
        rows = int(np.ceil(np.sqrt(num_charts)))
        cols = int(np.ceil(num_charts / rows))

    fig, axs = plt.subplots(
        rows, cols, subplot_kw=dict(projection="polar"), figsize=(6 * cols, 6 * rows)
    )
    axs = np.array(axs).flatten()  # Flatten para fácil indexação

    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    angles = np.append(angles, angles[0])  # Adiciona o primeiro ângulo ao final

    for i, data in enumerate(data_list):
        ax = axs[i]

        # Ajustar os dados para fechar o gráfico polar
        data["x_data"] = np.append(
            data["x_data"], data["x_data"][0]
        )  # Adiciona o primeiro ponto ao final
        data["y_data"] = np.append(
            data["y_data"], data["y_data"][0]
        )  # Adiciona o primeiro ponto ao final

        # Gráfico para dados masculinos
        ax.fill(
            angles,
            data["x_data"],
            color="#90EE90",  # Verde claro
            alpha=0.5,
            label=f'{data["x_label"]}',
        )
        ax.plot(
            angles,
            data["x_data"],
            color="#32CD32",  # Verde mais escuro
            linestyle="-",
            marker="o",
            markersize=4,
        )

        # Gráfico para dados femininos
        ax.fill(
            angles,
            data["y_data"],
            color="#FFB6C1",  # Rosa claro
            alpha=0.5,
            label=f'{data["y_label"]}',
        )
        ax.plot(
            angles,
            data["y_data"],
            color="#FF69B4",  # Rosa mais escuro
            linestyle="-",
            marker="o",
            markersize=4,
        )

        # Configurações do gráfico
        ax.set_title(data["variable_name"])

        radial_ticks = 10

        # Aplicação de labels personalizadas ou ângulos padrão
        if labels:
            ax.set_xticks(angles)
            ax.set_xticklabels(labels, fontsize=8)
        else:
            ax.set_xticks(angles)
            ax.set_xticklabels([f"{int(np.degrees(a))}°" for a in angles], fontsize=8)

        # Configuração de marcações radiais
        max_value = max(max(data["x_data"]), max(data["y_data"]))
        ax.set_yticks(np.linspace(0, max_value, radial_ticks))
        ax.yaxis.grid(True, linestyle="--", linewidth=0.5)
        # ax.set_yticklabels([f"{tick:.2f}" for tick in np.linspace(0, max_value, radial_ticks)], fontsize=8)

        # Exibição de ylabels centralizadas
        radial_labels = [
            f"{tick:.1f}" for tick in np.linspace(0, max_value, radial_ticks)
        ]
        ax.set_yticklabels([""] * len(radial_labels))  # Oculta as ylabels padrão
        for tick, label in zip(np.linspace(0, max_value, radial_ticks), radial_labels):
            ax.text(
                np.pi / 2.0,
                tick,
                label,
                ha="center",
                va="bottom",
                fontsize=8,
                color="black",
                weight="bold",
            )

        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    # Remove os subplots vazios
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Gráfico salvo em: {save_path}")
    else:
        plt.show()
