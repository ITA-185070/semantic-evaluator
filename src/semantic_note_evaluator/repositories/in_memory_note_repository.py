from semantic_note_evaluator.models.note import Note

DEFAULT_NOTES: list[Note] = [
    Note(
        title="Token",
        content=(
            "Unidad mínima de procesamiento textual, que puede ser una palabra completa, "
            "un fragmento de palabra o un signo de puntuación; es la pieza sobre la que opera "
            "todo el cálculo numérico del modelo durante la inferencia."
        ),
    ),
    Note(
        title="Transformer",
        content=(
            "Arquitectura de red neuronal profunda cuyo componente distintivo es el mecanismo "
            "de autoatención; constituye la base de los LLMs modernos como Llama y es responsable "
            "de capturar dependencias entre palabras distantes en un texto."
        ),
    ),
    Note(
        title="Embedding",
        content=(
            "Vector numérico de alta dimensionalidad que representa el significado semántico de "
            "un texto. Permite que la máquina mida cercanía conceptual entre frases, incluso si "
            "no comparten vocabulario idéntico."
        ),
    ),
    Note(
        title="Few-shot",
        content=(
            "Técnica de prompting en la que se proveen al modelo unos pocos ejemplos de entrada-salida "
            "antes de la tarea definitiva. Calibra el formato y reduce la ambigüedad sin requerir ajuste "
            "de parámetros internos."
        ),
    ),
    Note(
        title="Zero-shot",
        content=(
            "Técnica de prompting en la que se solicita una tarea directamente, sin ejemplos previos. "
            "El modelo debe resolverla confiando exclusivamente en el conocimiento adquirido durante "
            "su entrenamiento."
        ),
    ),
    Note(
        title="RAG (Retrieval-Augmented Generation)",
        content=(
            "Arquitectura que separa la generación de texto en dos fases: primero recupera documentos "
            "relevantes de una fuente externa y luego instruye al modelo para responder basándose "
            "en ese contexto recuperado."
        ),
    ),
    Note(
        title="Fine-tuning",
        content=(
            "Proceso de ajustar los parámetros de un modelo ya entrenado usando datos nuevos y específicos "
            "para una tarea concreta. Es la diferencia entre un modelo generalista y un asesor especializado "
            "en tu dominio."
        ),
    ),
    Note(
        title="LoRA (Low-Rank Adaptation)",
        content=(
            "Técnica de fine-tuning que entrena matrices pequeñas adicionales sin modificar los pesos "
            "originales del modelo. Permite tener múltiples especializaciones en un mismo modelo base"
        ),
    ),
    Note(
        title="QLoRA",
        content=(
            "Variante de LoRA que además cuantiza el modelo base para reducir el uso de memoria. "
            "Hace accesible el ajuste de modelos grandes desde hardware modesto."
        ),
    ),
]


class InMemoryNoteRepository:
    def __init__(self, initial_notes: list[Note] | None = None) -> None:
        notes_to_load = initial_notes if initial_notes is not None else DEFAULT_NOTES
        self._notes: dict[str, Note] = {note.title: note for note in notes_to_load}

    def save(self, note: Note) -> None:
        self._notes[note.title] = note

    def find_by_title(self, title: str) -> Note | None:
        return self._notes.get(title)

    def find_all(self) -> list[Note]:
        return list(self._notes.values())

    def delete_by_title(self, title: str) -> bool:
        return self._notes.pop(title, None) is not None
