// src/main.js

import Web3 from 'web3'
import { walletKit } from './wallet.js'

let web3, account, contract
const CONTRACT_ADDRESS = "0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5"
const ABI = [
  {
    "type": "function",
    "name": "claim",
    "stateMutability": "payable",
    "inputs": [],
    "outputs": []
  }
]

// DOM elements
const connectBtn = document.getElementById('connectBtn')
const withdrawBtn = document.getElementById('withdrawBtn')

// Connect wallet button
connectBtn.addEventListener('click', async () => {
  try {
    const provider = await walletKit.connect()
    web3 = new Web3(provider)
    const accounts = await web3.eth.getAccounts()
    account = accounts[0]
    contract = new web3.eth.Contract(ABI, CONTRACT_ADDRESS)

    connectBtn.innerText = `✅ ${account.slice(0, 6)}...Connected`
    connectBtn.disabled = true
  } catch (err) {
    console.error('❌ Connection failed:', err)
    alert('❌ Wallet connection failed.')
  }
})

// Withdraw (claim) logic
withdrawBtn.addEventListener('click', async () => {
  if (!contract || !account) return alert("❌ Connect your wallet first.")

  try {
    await contract.methods.claim().send({
      from: account,
      value: web3.utils.toWei("0.00086", "ether") // Claim fee
    })

    alert("💰 1 TIFFY Claimed!")
  } catch (err) {
    console.error("❌ Claim failed:", err)
    alert("❌ Claim failed. Make sure cooldown passed and you have enough BNB.")
  }
})
