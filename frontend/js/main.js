/**
 * Prompt Difficulty Predictor - Frontend Logic
 */

const examplePrompts = [
  {
    title: "Palíndromo (Fácil)",
    prompt:
      "Escribe una función en Python llamada `is_palindrome(s)` que reciba una cadena de texto y determine si es un palíndromo (se lee igual al derecho y al revés), ignorando mayúsculas y espacios.",
  },
  {
    title: "Dos Sumas / Two Sum (Medio)",
    prompt:
      "Dado un arreglo de números enteros `nums` y un entero `target`, retorna los índices de los dos números que sumen `target`.\nPuedes asumir que cada entrada tendrá exactamente una solución y no puedes usar el mismo elemento dos veces. Complejidad esperada: O(n).",
  },
  {
    title: "Segment Tree / Árbol de Segmentos (Difícil)",
    prompt:
      "Implementa una estructura de datos de Segment Tree con Lazy Propagation en C++ que soporte dos operaciones en un arreglo de tamaño N:\n1. Actualización de rango: sumar un valor val a todos los elementos en [L, R].\n2. Consulta de rango: calcular el máximo común divisor (MCD) de todos los elementos en [L, R]. Ambas operaciones deben ejecutarse en O(log N).",
  },
  {
    title: "Problema No Solucionable por Llama 3 8B (Cannot Solve)",
    prompt:
      "Diseña y prueba formalmente un algoritmo distribuido bizantino tolerante a fallos asíncrono óptimo bajo particiones de red severas que resuelva consenso estricto en menos de 2 rondas sin supuestos de sincronía parcial, e incluye la prueba de corrección en Coq con extracción de código verificable.",
  },
];

let exampleIndex = 0;

/**
 * Carga un prompt de ejemplo cíclicamente en el textarea
 */
function loadExamplePrompt() {
  const input = document.getElementById("inputText");
  const example = examplePrompts[exampleIndex];
  input.value = example.prompt;
  exampleIndex = (exampleIndex + 1) % examplePrompts.length;
  input.focus();
}

/**
 * Limpia la entrada y restaura el estado visual
 */
function clearAll() {
  const input = document.getElementById("inputText");
  input.value = "";
  input.focus();

  const outputContainer = document.getElementById("output");
  const noneInfo = document.getElementById("noneinfo");
  const result = document.getElementById("result");
  const resultText = document.getElementById("resultText");

  resultText.innerHTML = "";
  result.style.display = "none";
  noneInfo.style.display = "flex";
  outputContainer.classList.add("none");
}

/**
 * Copia el veredicto o resultado al portapapeles
 */
async function copyToClipboard() {
  const resultText = document.getElementById("resultText");
  const copyBtn = document.getElementById("copyButton");

  if (!resultText.innerText.trim()) return;

  try {
    await navigator.clipboard.writeText(resultText.innerText);
    const originalText = copyBtn.innerText;
    copyBtn.innerText = "¡Copiado!";
    copyBtn.style.borderColor = "var(--status-easy)";
    copyBtn.style.color = "var(--status-easy)";

    setTimeout(() => {
      copyBtn.innerText = originalText;
      copyBtn.style.borderColor = "";
      copyBtn.style.color = "";
    }, 2000);
  } catch (err) {
    console.error("Error al copiar al portapapeles:", err);
  }
}

/**
 * Heurística preliminar de frontend para predecir dificultad
 * (será complementada/reemplazada por el endpoint backend en el siguiente paso)
 */
function estimatePromptDifficultyLocally(prompt) {
  const text = prompt.toLowerCase();
  const wordCount = prompt.trim().split(/\s+/).length;
  const lineCount = prompt.split("\n").length;

  // Criterios simples basados en vocabulario y extensión
  const hardKeywords = [
    "coq",
    "bizantino",
    "consenso",
    "np-hard",
    "lazy propagation",
    "segment tree",
    "bitmask",
    "computational geometry",
    "polinomial",
  ];
  const mediumKeywords = [
    "o(n)",
    "o(log n)",
    "árbol",
    "grafo",
    "dinámica",
    "two sum",
    "recursivo",
    "ordenamiento",
    "binary search",
  ];

  let difficulty = "Medium";
  let badgeClass = "medium";
  let successRate = 65.0;
  let description =
    "El prompt presenta un nivel de complejidad intermedio. Llama 3 8B suele resolverlo con pruebas de código moderadas.";

  const hasHard = hardKeywords.some((k) => text.includes(k));
  const hasMedium = mediumKeywords.some((k) => text.includes(k));

  if (text.includes("bizantino") || text.includes("coq") || wordCount > 150) {
    difficulty = "Cannot Solve";
    badgeClass = "cannot-solve";
    successRate = 0.0;
    description =
      "El prompt excede las capacidades de razonamiento o verificación de Llama 3 8B. Tasa de éxito nula en pruebas automatizadas.";
  } else if (hasHard || wordCount > 80) {
    difficulty = "Hard";
    badgeClass = "hard";
    successRate = 22.5;
    description =
      "Complejidad algorítmica elevada. Llama 3 8B tiene una tasa de éxito reducida en la primera generación.";
  } else if (!hasMedium && wordCount < 30) {
    difficulty = "Easy";
    badgeClass = "easy";
    successRate = 94.0;
    description =
      "Tarea algorítmica básica. Llama 3 8B genera soluciones funcionales que aprueban los casos de prueba con alta probabilidad.";
  }

  return {
    difficulty,
    badgeClass,
    successRate,
    wordCount,
    lineCount,
    description,
    targetModel: "Llama 3 8B",
  };
}

/**
 * Renderiza el resultado en la tarjeta
 */
function renderResult(data) {
  const resultText = document.getElementById("resultText");
  const noneInfo = document.getElementById("noneinfo");
  const result = document.getElementById("result");
  const outputContainer = document.getElementById("output");

  resultText.innerHTML = `
    <div class="result-header">
      <div class="result-label">Dificultad Estimada</div>
      <div class="difficulty-badge ${data.badgeClass}">${data.difficulty}</div>
    </div>

    <div class="result-metrics">
      <div class="metric-row">
        <span class="metric-name">Modelo Objetivo</span>
        <span class="metric-val">${data.targetModel}</span>
      </div>
      <div class="metric-row">
        <span class="metric-name">Tasa Éxito Esperada</span>
        <span class="metric-val">${data.successRate.toFixed(1)}%</span>
      </div>
      <div class="metric-row">
        <span class="metric-name">Palabras en Prompt</span>
        <span class="metric-val">${data.wordCount}</span>
      </div>
      <div class="metric-row">
        <span class="metric-name">Líneas</span>
        <span class="metric-val">${data.lineCount}</span>
      </div>
    </div>

    <p class="result-description">${data.description}</p>
  `;

  noneInfo.style.display = "none";
  result.style.display = "flex";
  outputContainer.classList.remove("none");
}

/**
 * Consulta el endpoint de predicción del backend FastAPI
 */
async function callPredictionAPI(prompt) {
  const candidates = [
    "/api/v1/predict",
    "http://localhost:8000/api/v1/predict",
    "http://127.0.0.1:8000/api/v1/predict",
  ];

  for (const url of candidates) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt, model_target: "llama3-8b" }),
      });
      if (response && response.ok) {
        return await response.json();
      }
    } catch {
      // Intenta el siguiente candidato si este falló por red o CORS
      continue;
    }
  }
  return null;
}

/**
 * Ejecuta la predicción conectando con el backend FastAPI
 */
async function predictDifficulty() {
  const input = document.getElementById("inputText");
  const prompt = input.value.trim();

  if (!prompt) {
    alert("Por favor, ingrese un prompt de programación para evaluar.");
    input.focus();
    return;
  }

  const predictBtn = document.getElementById("predictBtn");
  const originalBtnText = predictBtn.innerText;
  predictBtn.disabled = true;
  predictBtn.innerText = "Analizando...";

  try {
    const data = await callPredictionAPI(prompt);

    if (data) {
      const badgeMap = {
        Easy: "easy",
        Medium: "medium",
        Hard: "hard",
        "Cannot Solve": "cannot-solve",
      };
      renderResult({
        difficulty: data.difficulty,
        badgeClass: badgeMap[data.difficulty] || "medium",
        successRate: data.estimated_success_rate ?? 50.0,
        wordCount: data.details?.word_count ?? prompt.split(/\s+/).length,
        lineCount: data.details?.line_count ?? prompt.split("\n").length,
        description: data.details?.description || "Predicción generada por el backend API.",
        targetModel: data.model_target || "Llama 3 8B",
      });
    } else {
      // Fallback local en caso de que el backend no esté accesible
      const localData = estimatePromptDifficultyLocally(prompt);
      renderResult(localData);
    }
  } catch (error) {
    console.error("Error en la predicción:", error);
    const localData = estimatePromptDifficultyLocally(prompt);
    renderResult(localData);
  } finally {
    predictBtn.disabled = false;
    predictBtn.innerText = originalBtnText;
  }
}
