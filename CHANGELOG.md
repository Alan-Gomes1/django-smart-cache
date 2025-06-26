# Changelog

## Histórico de Mudanças

## [0.1.1] - 2025-06-26
### Adicionado
- Compatibilidade ampliada para Django 4.2 e 5.0.
- Documentação detalhada no README.md, incluindo instruções de configuração e exemplos de uso.
- Orientação sobre importação de views/viewsets no método `ready` do apps.py para correto funcionamento dos decorators de cache.

### Alterado
- Dependências agora aceitam versões maiores ou iguais a Django 2.2 e DRF 3.10.

## [0.1.0] - 2024-06-25
### Adicionado
- Primeira versão da biblioteca.
- Decorators para cache automático em views e viewsets do Django/DRF.
- Invalidação automática de cache ao alterar modelos relacionados.
- Suporte a cache por usuário/token.
- Testes automatizados com pytest e pytest-django.
