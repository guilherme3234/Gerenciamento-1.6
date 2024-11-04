from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from .forms import FormLogin, formCadastroUsuario, InventarioForm, SalaForm
from .models import Senai
from django.contrib.auth.models import User, Group
from .models import Inventario, Sala
from django.core.cache import cache
from django.http import HttpResponse
from .models import Inventario
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout



# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')

def login(request):
    return render(request, 'login.html')


def profile(request):
    return render(request, 'profile.html')

def faq(request):
    return render(request, 'faq.html')

from django.contrib.auth.models import Group


#logouut 
def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required
def welcomeHomepage(request):
    # Verifica se o usuário pertence a um grupo específico
    is_coordenador = request.user.groups.filter(name="Coordenador").exists()
    is_professor = request.user.groups.filter(name="Professor").exists()

    # Filtra as salas de acordo com o grupo
    if is_coordenador:
        sala = Sala.objects.all()  # Coordenador vê todas as salas
    elif is_professor:  
        sala = Sala.objects.filter(responsavel=request.user.username)  # Professor vê sua sala específica
    else:
        sala = []  # Usuário sem grupo relevante não vê nada

    # Gerenciamento de formulário (se aplicável)
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('welcomeHomepage')
    else:
        form = SalaForm()

    # Renderizar a página com o contexto adequado
    return render(request, 'welcomeHomepage.html', {
        'form': form,
        'sala': sala,
        'is_coordenador': is_coordenador,
        'is_professor': is_professor,
    })




# Importar o modelo de itens (substitua Item pelo nome correto do seu modelo)


#---------------------------- CRUD DE SALAS ----------------------------
@login_required
def buscar_salas(request):
    context = {}
    query = request.GET.get('q')
    ordem = request.GET.get('ordem')
    is_coordenador = request.user.groups.filter(name="Coordenador").exists()
    is_professor = request.user.groups.filter(name="Professor").exists()

    sala = Sala.objects.all()

    if query:
        sala = sala.filter(sala__icontains=query)
    
    if ordem:
        sala = sala.order_by('sala' if ordem == 'A-Z' else '-sala')

    context['sala'] = sala
    form = SalaForm()
    context['form'] = form
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor

    return render(request, 'salas.html', context)




@login_required
def buscar_itens_sala(request):
    context = {}
    query = request.GET.get('q')  
    ordem = request.GET.get('ordem')  
    sala = request.GET.get('sala') 
    is_coordenador = request.user.groups.filter(name="Coordenador").exists()
    is_professor = request.user.groups.filter(name="Professor").exists() 

    inventario = Inventario.objects.all()

    if query:
        inventario = inventario.filter(num_inventario__icontains=query)
    
    if ordem:
        inventario = inventario.order_by('denominacao' if ordem == 'A-Z' else '-denominacao')

    if sala:
        inventario = inventario.filter(sala__icontains=sala)

    context['inventario'] = inventario
    form = InventarioForm()
    context['form'] = form
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor

    return render(request, 'itens.html', context)

@login_required
def adicionar_salas(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('welcomeHomepage')
    else:
        form = SalaForm()

    sala = Sala.objects.all()
    
    return render(request, 'welcomeHomepage.html', {'form': form, 'sala': sala})
@login_required
def update_sala(request):
    if request.method == 'POST':
        sala = request.POST.get('sala')
        
        # Busca a sala no banco de dados
        sala = get_object_or_404(Sala, sala=sala)

        # Atualiza os valores com base nos dados do formulário
        sala.descricao = request.POST.get('descricao')
        sala.localizacao = request.POST.get('localizacao')
        sala.link_imagem = request.POST.get('link_imagem')	
        sala.responsavel = request.POST.get('responsavel')
        sala.quantidade_itens = request.POST.get('quantidade_itens')
        sala.email_responsavel = request.POST.get('email_responsavel')
        sala.save()

        # Redireciona de volta à página de salas ou para onde você quiser
        return redirect('salas')  

    return HttpResponse("Método não permitido.", status=405)
@login_required
def excluir_sala(request):
    if request.method == 'POST':
        sala = request.POST.get('sala')
        
        # Exclui a sala com base no nome
        try:
            sala = Sala.objects.get(sala=sala)
            sala.delete()
            return redirect('salas')  # Redireciona para a lista de salas após exclusão
        except Sala.DoesNotExist:
            return HttpResponse("Sala não encontrada.", status=404)

@login_required
def salas(request):
    # Verifica os grupos do usuário
    is_coordenador = request.user.groups.filter(name="Coordenador").exists()
    is_professor = request.user.groups.filter(name="Professor").exists()

    # Filtra as salas com base no grupo do usuário
    if is_coordenador:
        sala = Sala.objects.all()  # Coordenador vê todas as salas
    elif is_professor:
        sala = Sala.objects.filter(responsavel=request.user.username)  # Professor vê apenas suas salas
    else:
        sala = []  # Usuário sem permissão não vê nada

    # Gerenciamento de formulário (caso aplicável)
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('salas')  # Redireciona para a página de salas
    else:
        form = SalaForm()

    # Renderiza a página 'salas.html' com o contexto adequado
    return render(request, 'salas.html', {
        'form': form,
        'sala': sala,
        'is_coordenador': is_coordenador,
        'is_professor': is_professor,
    })


#---------------------------- LOGIN E CADASTRO DE USUÁRIO ----------------------------
@login_required
def cadastroUsuario(request):
    context = {}
    dadosSenai = Senai.objects.all()
    context["dadosSenai"] = dadosSenai
    
    if request.method == 'POST':
        form = formCadastroUsuario(request.POST)
        if form.is_valid():
            var_nome = form.cleaned_data['first_name']
            var_sobrenome = form.cleaned_data['last_name']
            var_usuario = form.cleaned_data['user']
            var_email = form.cleaned_data['email']
            var_senha = form.cleaned_data['password']
            var_grupo = form.cleaned_data['group']  # Captura o grupo selecionado
            var_sala = form.cleaned_data['sala']  # Captura a sala selecionada
            # Cria o usuário
            user = User.objects.create_user(username=var_usuario, email=var_email, password=var_senha)
            user.first_name = var_nome
            user.last_name = var_sobrenome
            user.save()

            # Atribui o usuário ao grupo selecionado
            grupo = Group.objects.get(name=var_grupo)
            user.groups.add(grupo)
            

            return redirect('/welcomeHomepage')
            print('Cadastro realizado com sucesso')
    else:
        form = formCadastroUsuario()
        context['form'] = form
        print('Cadastro falhou')
    
    return render(request, 'cadastroUsuario.html', context)

def login(request):
    context = {}
    dadosSenai = Senai.objects.all()
    context["dadosSenai"] = dadosSenai
    if request.method == 'POST':
        form = FormLogin(request.POST)
        if form.is_valid():

            var_usuario = form.cleaned_data['user']
            var_senha = form.cleaned_data['password']
            
            user = authenticate(username=var_usuario, password=var_senha)

            if user is not None:
                auth_login(request, user)
                return redirect('/welcomeHomepage')  
            else:
                print('Login falhou')
    else:
        form = FormLogin()
        context['form'] = form
        return render(request, 'login.html', context)
    

#---------------------------- CRUD DE INVENTÁRIO ----------------------------
@login_required
def itens(request):
    inventario = Inventario.objects.all()
    item_especifico = inventario.first()  # ou qualquer outro critério para escolher o item
    is_coordenador = request.user.groups.filter(name="Coordenador").exists()
    is_professor = request.user.groups.filter(name="Professor").exists()
   
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('itens')  # Redireciona para a página de itens
    else:
        form = InventarioForm()
    
    return render(request, 'itens.html', {'form': form, 'inventario': inventario, 'item_especifico': item_especifico, 'is_coordenador': is_coordenador, 'is_professor': is_professor})

@login_required
def adicionar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar para a rota inicial, independente de onde estava
    else:
        form = InventarioForm()
    
    # Se precisar listar todos os itens no modal de adição, inclua isso:
    inventario = Inventario.objects.all()
    
    return render(request, 'itens.html', {'form': form, 'inventario': inventario})

@login_required
def buscar_itens(request):
    context = {}
    query = request.GET.get('q')  # Pega o valor do campo de busca
    ordem = request.GET.get('ordem')  # Pega o valor da ordem A-Z ou Z-A
    sala = request.GET.get('sala')  # Pega o valor da sala
    is_coordenador = request.user.groups.filter(name="Coordenador").exists()
    is_professor = request.user.groups.filter(name="Professor").exists()

    inventario = Inventario.objects.all()

    if query:
        inventario = inventario.filter(num_inventario__icontains=query)
    
    if ordem:
        if ordem == 'A-Z':
            inventario = inventario.order_by('denominacao')
        elif ordem == 'Z-A':
            inventario = inventario.order_by('-denominacao')

    if sala:
        inventario = inventario.filter(sala__icontains=sala)

    context['inventario'] = inventario
    form = InventarioForm()
    context['form'] = form
    context['is_coordenador'] = is_coordenador
    context['is_professor'] = is_professor
    
    return render(request, 'itens.html', context)





@login_required
def update_item(request):
    if request.method == 'POST':
        num_inventario = request.POST.get('numInventario')
        
        # Busca o item no banco de dados
        item = get_object_or_404(Inventario, num_inventario=num_inventario)

        # Atualiza os valores com base nos dados do formulário
        item.denominacao = request.POST.get('denominacao')
        item.localizacao = request.POST.get('localizacao')
        item.sala = request.POST.get('sala')
        item.link_imagem = request.POST.get('imagem')
        item.save()

        # Redireciona de volta à página de itens ou para onde você quiser
        return redirect('itens')  

    return HttpResponse("Método não permitido.", status=405)
@login_required
def excluir_inventario(request):
    if request.method == 'POST':
        num_inventario = request.POST.get('numInventario')
        
        # Exclui o item com base no número de inventário
        try:
            item = Inventario.objects.get(num_inventario=num_inventario)
            item.delete()
            return redirect('itens')  # Redireciona para a lista de itens após exclusão
        except Inventario.DoesNotExist:
            return HttpResponse("Item não encontrado.", status=404)
        




#---------------------------- PROFILE ----------------------------
@login_required
def profile(request):
    user = request.user  # Obter o usuário logado
    
    context = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'id': user.id,
        'sala': sala.sala if sala else 'Nenhuma sala atribuída',
    }
    
    return render(request, 'profile.html', context)

@login_required
def profile(request):
    user = request.user
    sala = Sala.objects.filter(responsavel=user).first()  # Assume que 'responsavel' é o campo que liga o usuário à sala

    if request.method == 'POST':
        # Coleta os valores postados pelas modais, se forem enviados
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)

        # Atualiza os campos do usuário com os novos valores
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Opcional: Mensagem de sucesso (se 'messages' estiver configurado no projeto)
        from django.contrib import messages
        messages.success(request, "Perfil atualizado com sucesso.")

    context = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'id': user.id,
        'sala': sala.sala if sala else "Nenhuma sala atribuída",
    }

    return render(request, 'profile.html', context)

@login_required
def profile(request):
    user = request.user  # Usuário logado
    
    # Buscar a sala associada ao usuário através do campo 'responsavel'
    sala = Sala.objects.filter(responsavel=user.username).first()  # Verifica se o username do usuário corresponde ao 'responsavel'
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)

        # Atualiza o usuário com os novos valores
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        from django.contrib import messages
        messages.success(request, "Perfil atualizado com sucesso.")
    
    # Prepara o contexto com os dados do perfil e da sala associada
    context = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'id': user.id,
        'sala': sala.sala if sala else "Nenhuma sala atribuída",  # Exibe o nome da sala ou uma mensagem padrão
    }

    return render(request, 'profile.html', context)

@login_required
def profile(request):
    user = request.user  # Obter o usuário logado
    
    # Buscar a sala onde o 'responsavel' seja o email do usuário logado
    sala_responsavel = Sala.objects.filter(responsavel=user.email).first()  # Usar 'first()' para pegar a primeira sala associada
    
    # Verificar se uma sala foi encontrada, e usar o nome da sala ou uma mensagem padrão
    if sala_responsavel:
        sala_nome = sala_responsavel.sala  # Atribuir o nome da sala associada
    else:
        sala_nome = "Nenhuma sala atribuída"
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)

        # Atualizar os dados do usuário
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        from django.contrib import messages
        messages.success(request, "Perfil atualizado com sucesso.")
    
    # Preparar o contexto para o template
    context = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'id': user.id,
        'sala': sala_nome,  # Passar o nome da sala para o template
    }

    return render(request, 'profile.html', context)

