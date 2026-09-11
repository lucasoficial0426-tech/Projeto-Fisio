import axios

# Configuração base da API
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api"

// Criação da instância do axios
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
})

// Interceptores para tratar erros
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // O servidor respondeu com um status de erro
            const { status, data } = error.response
            
            // Tratar erros específicos das regras de negócio
            if (status === 400 && data.detail && data.detail.includes("RN-")) {
                // Erro de regra de negócio
                console.error(`Regra de negócio violada: ${data.detail}`)
                throw new Error(data.detail)
            }
            
            // Outros erros
            console.error(`Erro ${status}: ${data.detail || "Erro desconhecido"}`)
            throw new Error(data.detail || "Erro desconhecido")
        } else if (error.request) {
            // A requisição foi feita mas não houve resposta
            console.error("Sem resposta do servidor")
            throw new Error("Sem resposta do servidor")
        } else {
            // Algo aconteceu na configuração da requisição
            console.error("Erro na configuração da requisição:", error.message)
            throw new Error(error.message)
        }
    }
)

export default api
