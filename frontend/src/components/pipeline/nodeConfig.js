// src/config/nodeConfigs.js

export const nodeFields = {
  'Données': [
    {
      key: 'format',
      label: 'Format',
      type: 'select',
      options: ['CSV', 'JSON', 'Parquet', 'Base de données']
    },
    { key: 'taille', label: 'Taille (Go)', type: 'number', placeholder: '2' },
    { key: 'echantillons', label: 'Échantillons', type: 'number', placeholder: '10000' }
  ],

  'Entrainement': [
    {
      key: 'modele',
      label: 'Modèle',
      type: 'select',
      options: ['CNN', 'RNN', 'Transformer', 'LSTM', 'GPT']
    },
    { key: 'parametres', label: 'Paramètres', type: 'number', placeholder: '28000' },
    { key: 'epochs', label: 'Epochs', type: 'number', placeholder: '300' },
    { key: 'batch_size', label: 'Batch size', type: 'number', placeholder: '50' }
  ],

  'Inférence': [
    {
      key: 'modele_utilise',
      label: 'Modèle utilisé',
      type: 'select',
      options: ['CNN', 'RNN', 'Transformer', 'LSTM']
    },
    { key: 'taille_lot', label: 'Taille du lot', type: 'number', placeholder: '1000' }
  ],

  'LLM Call': [
    {
      key: 'provider',
      label: 'Fournisseur',
      type: 'select',
      options: [
        'openai',
        'anthropic',
        'google',
        'meta',
        'mistralai',
        'cohere',
        'microsoft',
        'databricks'
      ]
    },
    {
      key: 'model',
      label: 'Modèle',
      type: 'select',
      dependsOn: 'provider',
      optionsMapping: {
        openai: [
          'chatgpt-4o-latest',
          'gpt-3.5-turbo',
          'gpt-4',
          'gpt-4-turbo',
          'gpt-4o',
          'gpt-4o-mini',
          'o1',
          'o1-mini'
        ],
        anthropic: [
          'claude-2.0',
          'claude-2.1',
          'claude-3-5-haiku-latest',
          'claude-3-5-sonnet-latest',
          'claude-3-7-sonnet-latest',
          'claude-3-haiku-20240307',
          'claude-3-opus-latest',
          'claude-3-sonnet-20240229'
        ],
        google: [
          'google/gemma-2-2b',
          'google/gemma-2-9b',
          'google/gemma-2-27b',
          'google/codegemma-2b',
          'google/codegemma-7b',
          'gemini-1.0-pro',
          'gemini-1.5-pro',
          'gemini-1.5-flash',
          'gemini-2.0-flash'
        ],
        meta: [
          'meta-llama/Meta-Llama-3.1-8B',
          'meta-llama/Meta-Llama-3.1-70B',
          'meta-llama/Meta-Llama-3.1-405B',
          'meta-llama/Meta-Llama-3-8B',
          'meta-llama/Meta-Llama-3-70B',
          'meta-llama/Llama-2-7b',
          'meta-llama/Llama-2-13b',
          'meta-llama/Llama-2-70b',
          'meta-llama/CodeLlama-7b-hf',
          'meta-llama/CodeLlama-13b-hf',
          'meta-llama/CodeLlama-34b-hf',
          'meta-llama/CodeLlama-70b-hf'
        ],
        mistralai: [
          'mistralai/Mistral-7B-v0.3',
          'mistralai/Mixtral-8x7B-v0.1',
          'mistralai/Mixtral-8x22B-v0.1',
          'mistralai/Codestral-22B-v0.1',
          'mistralai/Mathstral-7B-v0.1',
          'ministral-3b-latest',
          'ministral-8b-latest',
          'mistral-tiny',
          'mistral-small',
          'mistral-medium',
          'mistral-large-latest'
        ],
        cohere: [
          'c4ai-aya-expanse-8b',
          'c4ai-aya-expanse-32b',
          'command',
          'command-light',
          'command-r',
          'command-r-plus'
        ],
        microsoft: [
          'microsoft/phi-1',
          'microsoft/phi-1_5',
          'microsoft/Phi-3-mini-128k-instruct',
          'microsoft/Phi-3-small-128k-instruct',
          'microsoft/Phi-3-medium-128k-instruct'
        ],
        databricks: [
          'databricks/dolly-v1-6b',
          'databricks/dolly-v2-12b',
          'databricks/dolly-v2-7b',
          'databricks/dolly-v2-3b',
          'databricks/dbrx-base'
        ]
      }
    },
    { key: 'output_tokens', label: 'Tokens générés', type: 'number', placeholder: '100' },
    { key: 'request_latency', label: 'Latence (ms)', type: 'number', placeholder: '100' }
  ],

  'LLM Expert': [
    { key: 'active_params', label: 'Param. actifs (milliards)', type: 'number', placeholder: '7' },
    { key: 'total_params', label: 'Param. totaux (milliards)', type: 'number', placeholder: '10' },
    { key: 'output_tokens', label: 'Tokens générés', type: 'number', placeholder: '250' },
    { key: 'request_latency', label: 'Latence (ms)', type: 'number', placeholder: '100' },
    { key: 'mix_gwp', label: 'Mix GWP (kgCO2eq/kWh)', type: 'number', placeholder: '0.5088' },
    { key: 'mix_adpe', label: 'Mix ADPe (kgSbeq/kWh)', type: 'number', placeholder: '0.0000442' },
    { key: 'mix_pe', label: 'Mix PE (MJ/kWh)', type: 'number', placeholder: '4.484' }
  ]
}