import api from "./api"

class PacienteService {
    static async getAll(skip = 0, limit = 100) {
        try {
            const response = await api.get(`/pacientes/?skip=${skip}&limit=${limit}`)
            return response.data
        } catch (error) {
            throw error
        }
    }

    static async getById(id) {
        try {
            const response = await api.get(`/pacientes/${id}`)
            return response.data
        } catch (error) {
            throw error
        }
    }

    static async create(pacienteData) {
        try {
            const response = await api.post("/pacientes/", pacienteData)
            return response.data
        } catch (error) {
            throw error
        }
    }

    static async update(id, pacienteData) {
        try {
            const response = await api.put(`/pacientes/${id}`, pacienteData)
            return response.data
        } catch (error) {
            throw error
        }
    }

    static async delete(id) {
        try {
            await api.delete(`/pacientes/${id}`)
            return true
        } catch (error) {
            throw error
        }
    }

    static async getPacientesComPacotesAtivos() {
        try {
            const response = await api.get("/pacientes/com-pacotes-ativos/")
            return response.data
        } catch (error) {
            throw error
        }
    }

    static async searchByCpf(cpf) {
        try {
            const response = await api.get(`/pacientes/?cpf=${cpf}`)
            return response.data
        } catch (error) {
            throw error
        }
    }
}

export default PacienteService
