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
      options: ['openai', 'anthropic', 'google', 'mistral', 'cohere']
    },
      {
      key: 'model',
      label: 'Modèle',
      type: 'select',
      dependsOn: 'provider',                    
      optionsMapping: {                        
        'openai': ['gpt-4o', 'gpt-4-turbo'],
        'anthropic': ['claude-3-opus', 'claude-3-sonnet'],
        'google': ['gemini-pro'],
        'mistral': ['mistral-large'],
        'cohere': ['command-r-plus']
      }
    },
    { key: 'output_tokens', label: 'Tokens générés', type: 'number', placeholder: '100' },
    { key: 'request_latency', label: 'Latence (ms)', type: 'number', placeholder: '100' }
  ],

  'LLM Expert': [
    {
      key: 'provider',
      label: 'Fournisseur',
      type: 'select',
      options: ['openai', 'anthropic', 'google', 'mistral']
    },
     {
      key: 'model',
      label: 'Modèle',
      type: 'select',
      dependsOn: 'provider',
      optionsMapping: {
        'openai': ['gpt-4o'],
        'anthropic': ['claude-3-opus', 'claude-3-sonnet'],
        'google': ['gemini-ultra'],
        'mistral': ['mistral-large']
      }
    },
    { key: 'active_params', label: 'Param. actifs (milliards)', type: 'number', placeholder: '7' },
    { key: 'total_params', label: 'Param. totaux (milliards)', type: 'number', placeholder: '10' },
    { key: 'output_tokens', label: 'Tokens générés', type: 'number', placeholder: '250' },
    { key: 'request_latency', label: 'Latence (ms)', type: 'number', placeholder: '100' },
    { key: 'mix_gwp', label: 'Mix GWP (kgCO2eq/kWh)', type: 'number', placeholder: '0.5088' },
    { key: 'mix_adpe', label: 'Mix ADPe (kgSbeq/kWh)', type: 'number', placeholder: '0.0000442' },
    { key: 'mix_pe', label: 'Mix PE (MJ/kWh)', type: 'number', placeholder: '4.484' }
  ]
}