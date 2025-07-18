console.log("JS carregado!");

document.addEventListener("DOMContentLoaded", function () {
  // ================================
  // Seletores e Constantes Globais
  // ================================
  const correctionForm = document.getElementById("correctionForm");
  const submitButton = document.getElementById("submitButton");
  const buttonText = document.getElementById("buttonText");
  const spinner = document.getElementById("spinner");
  const feedback = document.getElementById("feedback");
  
  const tabButtons = document.querySelectorAll(".tab-button");
  const essayTextarea = document.getElementById("essay-textarea");
  const fileInput = document.getElementById("fileInput");
  const dropArea = document.getElementById("drop-area");
  
  const resultsSection = document.getElementById("results-section");
  const resultsContainer = document.getElementById("results-container");

  const themeToggle = document.getElementById("toggleTheme");
  const logoLight = document.querySelector(".logo-light");
  const logoDark = document.querySelector(".logo-dark");

  // Estado da Aplicação
  let currentInputMethod = 'text';

  // URL DA SUA API BACKEND LOCAL
  const API_URL = 'http://127.0.0.1:8000/correct/';

  // ================================
  // Lógica de Abas (Texto/Arquivo)
  // ================================
  tabButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      tabButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
      btn.classList.add("active");
      const tab = btn.getAttribute("data-tab");
      document.getElementById(tab + "-tab").classList.add("active");
      currentInputMethod = tab === "file" ? "file" : "text";
    });
  });

  // ================================
  // Dark Mode (Tema)
  // ================================
  if (themeToggle) {
    themeToggle.addEventListener("change", function () {
      document.body.classList.toggle("dark-mode", themeToggle.checked);
      if (logoLight && logoDark) {
        logoLight.style.display = themeToggle.checked ? "none" : "inline";
        logoDark.style.display = themeToggle.checked ? "inline" : "none";
      }
    });
  }

  // ================================
  // Drag and Drop para Upload de Arquivo
  // ================================
  if (dropArea && fileInput) {
    dropArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropArea.classList.add("dragover");
    });
    dropArea.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dropArea.classList.remove("dragover");
    });
    dropArea.addEventListener("drop", (e) => {
      e.preventDefault();
      dropArea.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
      }
    });
    dropArea.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) {
        mostrarFeedback(`Arquivo selecionado: ${fileInput.files[0].name}`, "#43766c", 3000);
      }
    });
  }

  // ================================
  // Lógica de Correção Principal
  // ================================
  async function handleCorrection(e) {
    e.preventDefault();
    iniciarEnvio();
    
    let essayText = '';
    
    try {
        if (currentInputMethod === 'text') {
            essayText = essayTextarea.value;
            if (!essayText.trim()) {
                throw new Error("Por favor, insira o texto da redação.");
            }
        } else { // 'file'
            const file = fileInput.files[0];
            if (!file) {
                throw new Error("Por favor, selecione um arquivo.");
            }
            mostrarFeedback("Extraindo texto do arquivo...", "#43766c", 10000);
            essayText = await extractTextFromFile(file);
            if (!essayText.trim()) {
                throw new Error("O arquivo parece estar vazio ou não contém texto legível.");
            }
        }
        
        mostrarFeedback("Analisando com a IA... Isso pode levar um momento.", "#43766c", 15000);
  
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: essayText })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Erro do servidor: ${errorData.detail || response.statusText}`);
        }

        const data = await response.json();
        displayFormattedResults(data.correction);

    } catch (error) {
      console.error('Erro na correção:', error);
      mostrarFeedback(error.message, "#e57373");
      finalizarEnvio();
    }
  }

  // ================================
  // Exibição de Resultados
  // ================================
  function displayFormattedResults(correctionText) {
    resultsContainer.innerHTML = `
      <h2 class="results-title fade-drop">Análise da Redação</h2>
      <div class="results-content fade-drop delay-1">
        ${correctionText.replace(/\n/g, '<br>')}
      </div>
    `;
    resultsSection.classList.add('visible');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    finalizarEnvio();
  }

  // ================================
  // Funções Auxiliares
  // ================================
  function iniciarEnvio() {
    buttonText.style.display = "none";
    spinner.style.display = "block";
    submitButton.disabled = true;
    submitButton.classList.add("pulsing");
    feedback.textContent = "";
    resultsSection.classList.remove("visible");
  }

  function finalizarEnvio() {
    buttonText.style.display = "block";
    spinner.style.display = "none";
    submitButton.disabled = false;
    submitButton.classList.remove("pulsing");
  }
  
  function mostrarFeedback(mensagem, cor, duracao = 5000) {
    feedback.textContent = mensagem;
    feedback.style.color = cor;
    feedback.classList.add("active");
    setTimeout(() => { feedback.classList.remove("active"); }, duracao);
  }
  
  async function extractTextFromFile(file) {
    // Exemplo para PDF e DOCX
    if (file.type === "application/pdf") {
      return await extractTextFromPDF(file);
    } else if (
      file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
      file.name.endsWith(".docx")
    ) {
      return await extractTextFromDocx(file);
    } else if (file.type.startsWith("text/") || file.name.endsWith(".txt")) {
      return await file.text();
    } else {
      throw new Error("Formato de arquivo não suportado.");
    }
  }

  async function extractTextFromPDF(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async function () {
        try {
          const typedarray = new Uint8Array(reader.result);
          const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
          let text = "";
          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const content = await page.getTextContent();
            text += content.items.map(item => item.str).join(" ") + "\n";
          }
          resolve(text);
        } catch (err) {
          reject("Erro ao extrair texto do PDF.");
        }
      };
      reader.onerror = () => reject("Erro ao ler o arquivo PDF.");
      reader.readAsArrayBuffer(file);
    });
  }

  async function extractTextFromDocx(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async function (event) {
        try {
          mammoth.extractRawText({ arrayBuffer: event.target.result })
            .then(result => resolve(result.value))
            .catch(() => reject("Erro ao extrair texto do DOCX."));
        } catch (err) {
          reject("Erro ao processar o arquivo DOCX.");
        }
      };
      reader.onerror = () => reject("Erro ao ler o arquivo DOCX.");
      reader.readAsArrayBuffer(file);
    });
  }

  // ================================
  // Event Listeners Principais
  // ================================
  if (correctionForm) correctionForm.addEventListener("submit", handleCorrection);

});