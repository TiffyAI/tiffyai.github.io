import { Web3Modal } from '@web3modal/html'
import { EthereumClient, w3mConnectors, w3mProvider } from '@web3modal/ethereum'
import { configureChains, createConfig, getAccount, disconnect, readContract, writeContract, watchAccount } from '@wagmi/core'
import { bsc } from 'viem/chains'

// --- Replace with your contract data ---
const contractAddress = '0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5'
const contractAbi = [
  {
    "type": "function",
    "name": "claim",
    "stateMutability": "payable",
    "inputs": [],
    "outputs": []
  }
]

// --- WalletConnect Project ID ---
const projectId = 'bf40c7dcdb05f06f2769573103007576'

// --- Configure chains & wagmi ---
const chains = [bsc]
const { publicClient } = configureChains(chains, [w3mProvider({ projectId })])
const wagmiConfig = createConfig({
  autoConnect: true,
  connectors: w3mConnectors({ projectId, chains }),
  publicClient
})

// --- Create Ethereum Client & Web3Modal ---
const ethereumClient = new EthereumClient(wagmiConfig, chains)
export const web3modal = new Web3Modal({ projectId, themeMode: 'dark' }, ethereumClient)

// --- Helpers ---
export const connectWallet = async () => {
  try {
    await web3modal.openModal()
  } catch (e) {
    console.error("Connect error:", e)
  }
}

export const getWalletAddress = () => {
  const account = getAccount()
  return account?.address || null
}

export const onWalletChange = (callback) => {
  watchAccount((acc) => callback(acc))
}

export const isWalletConnected = () => {
  return getAccount().isConnected
}

export const disconnectWallet = async () => {
  await disconnect()
}

// --- Claim function (used in Claim Portal) ---
export const claimTiffy = async () => {
  try {
    await writeContract({
      address: contractAddress,
      abi: contractAbi,
      functionName: 'claim',
      value: BigInt(860000000000000), // 0.00086 BNB
    })

    return { success: true }
  } catch (e) {
    console.error("Claim failed:", e)
    return { success: false, error: e }
  }
}
