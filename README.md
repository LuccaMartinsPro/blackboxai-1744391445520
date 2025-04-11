# FitConnect - Plataforma de Gestão de Treinos

FitConnect é uma plataforma web que conecta Personal Trainers, Alunos e Nutricionistas, permitindo uma gestão eficiente de treinos, acompanhamento de progresso e comunicação em tempo real.

## 🚀 Funcionalidades

### Para Personal Trainers
- Criar e gerenciar perfil profissional
- Adicionar e gerenciar alunos
- Criar planos de treino personalizados
- Associar vídeos aos exercícios
- Acompanhar progresso dos alunos
- Comunicação em tempo real com alunos
- Exportar planos em PDF

### Para Alunos
- Visualizar planos de treino
- Ver vídeos explicativos dos exercícios
- Marcar exercícios como concluídos
- Registrar progresso
- Comunicar-se com o personal trainer
- Acompanhar estatísticas de treino

### Para Nutricionistas
- Gerenciar perfil profissional
- Acompanhar pacientes
- Integração com planos de treino
- Comunicação com alunos e personal trainers

## 💻 Tecnologias Utilizadas

- **Frontend:**
  - HTML5
  - Tailwind CSS
  - JavaScript
  - Google Fonts
  - Font Awesome

- **Backend:**
  - Python
  - Flask
  - SQLite
  - Flask-CORS

## 🛠️ Instalação e Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/fitconnect.git
cd fitconnect
```

2. Instale as dependências do Python:
```bash
pip install -r requirements.txt
```

3. Inicie o servidor:
```bash
python server.py
```

4. Abra o navegador e acesse:
```
http://localhost:8000
```

## 📁 Estrutura do Projeto

```
fitconnect/
├── pages/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   ├── trainer-dashboard.html
│   │   ├── student-dashboard.html
│   │   └── nutritionist-dashboard.html
│   ├── workouts/
│   │   └── create-plan.html
│   ├── chat/
│   │   └── chat.html
│   └── profile/
│       └── profile.html
├── server.py
├── requirements.txt
└── README.md
```

## 🔐 Segurança

- Autenticação de usuários
- Proteção de rotas
- Validação de relacionamentos (aluno-personal)
- Criptografia de senhas
- Sessões seguras

## 🌟 Recursos Adicionais

- Design responsivo
- Interface moderna e intuitiva
- Modo escuro
- Notificações em tempo real
- Upload de imagens
- Integração com vídeos do YouTube

## 📱 Compatibilidade

A plataforma é totalmente responsiva e funciona em:
- Computadores
- Tablets
- Smartphones

## 🤝 Contribuição

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Faça o Commit de suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Faça o Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte, envie um email para support@fitconnect.com ou abra uma issue no GitHub.

## ✨ Próximos Passos

- [ ] Implementação de pagamentos
- [ ] App mobile
- [ ] Integração com dispositivos wearables
- [ ] Videoconferência integrada
- [ ] Análise avançada de dados
- [ ] Gamificação

## 🎯 Status do Projeto

O projeto está em desenvolvimento ativo e aberto para contribuições.

---

Desenvolvido com ❤️ pela equipe FitConnect
