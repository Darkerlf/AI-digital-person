import localLoginBackground from '../assets/lingshan-login-bg.jpg'

const configuredLoginBackground = import.meta.env.VITE_LOGIN_BACKGROUND_URL?.trim()

export const loginBackground = configuredLoginBackground || localLoginBackground
