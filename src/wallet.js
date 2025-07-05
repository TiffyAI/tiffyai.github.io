import { Core } from '@walletconnect/core'
import { WalletKit } from '@reown/walletkit'

const core = new Core({
  projectId: 'bf40c7dcdb05f06f2769573103007576' // your actual WalletConnect project ID
})

const metadata = {
  name: 'TiffyAI',
  description: `Decentralized Wealth.
TiffyAI is a hyper-intelligent Web3 ecosystem merging AI-powered tools, tokenized rewards, and gamified finance.`,
  url: 'https://tiffyai.github.io', // this must match your live domain
  icons: ['https://imagedelivery.net/_aTEfDRm7z3tKgu9JhfeKA/ddc202a2-e490-4cfe-2481-52e3ae276400/sm']
}

export const walletKit = await WalletKit.init({
  core,
  metadata
})
