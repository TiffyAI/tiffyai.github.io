// src/wallet.js

import { Core } from '@walletconnect/core'
import { WalletKit } from '@reown/walletkit'

const core = new Core({
  projectId: 'bf40c7dcdb05f06f2769573103007576'
})

const metadata = {
  name: 'TiffyAI Miner',
  description: 'Mine TiffyAI and Claim your rewards',
  url: 'https://tiffyai.github.io/Mining-Machine-/', // ✅ this must match the verified domain
  icons: ['https://tiffyai.github.io/TiffyAI-Token.png']
}

export const walletKit = await WalletKit.init({ core, metadata })
