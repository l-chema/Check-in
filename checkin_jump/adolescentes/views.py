from datetime import date, datetime
from django.shortcuts import render, get_object_or_404, redirect
from .models import Adolescente, DiaEvento, Presenca, PequenoGrupo
from .forms import AdolescenteForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required, permission_required

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("listar_adolescentes")  # Redireciona para a lista após login
        else:
            messages.error(request, "Usuário ou senha inválidos. Por favor, verifique suas credenciais e tente novamente.")


    return render(request, "adolescentes/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")  # Redireciona para a tela de login após logout

@login_required
def listar_adolescentes(request):
    adolescentes = Adolescente.objects.all()
    return render(request, 'adolescentes/listar.html', {'adolescentes': adolescentes})

@login_required
def pagina_checkin(request):
    return render(request, 'checkin.html')

@login_required
def pagina_pgs(request):
    return render(request, 'pgs.html')

@login_required
def criar_adolescente(request):
    if request.method == "POST":
        form = AdolescenteForm(request.POST, request.FILES)
        if form.is_valid():
            # Verifica se a data de nascimento não é futura
            data_nascimento = form.cleaned_data['data_nascimento']
            if data_nascimento > datetime.now().date():
                messages.error(request, "A data de nascimento não pode ser no futuro.")
                return redirect('criar_adolescente')

            form.save()
            return redirect('listar_adolescentes')
    else:
        form = AdolescenteForm()
    return render(request, 'adolescentes/criar_adolescente.html', {'form': form})

@login_required
def editar_adolescente(request, id):
    adolescente = get_object_or_404(Adolescente, id=id)
    if request.method == "POST":
        form = AdolescenteForm(request.POST, request.FILES, instance=adolescente)
        if form.is_valid():
            form.save()
            return redirect('listar_adolescentes')
    else:
        form = AdolescenteForm(instance=adolescente)
    return render(request, 'adolescentes/criar_adolescente.html', {'form': form})

@login_required
def excluir_adolescente(request, id):
    adolescente = get_object_or_404(Adolescente, id=id)
    if request.method == "POST":
        adolescente.delete()
        return redirect('listar_adolescentes')
    return render(request, 'adolescentes/confirmar_exclusao.html', {'adolescente': adolescente})

@login_required
def lista_dias_evento(request):
    dias = DiaEvento.objects.all().order_by('-data')
    return render(request, 'checkin/lista_dias.html', {'dias': dias})

@login_required
@permission_required('checkin.add_diaevento', raise_exception=True)
def adicionar_dia_evento(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        if DiaEvento.objects.filter(data=data).exists():
            messages.warning(request, "Esse dia já foi adicionado.")
        if data and datetime.strptime(data, "%Y-%m-%d").date() < date.today():
            messages.warning(request, "Não é possível adicionar um dia no passado.")
        else:
            DiaEvento.objects.create(data=data)
        return redirect('pagina_checkin')
    return render(request, 'checkin/adicionar_dia.html')

@login_required
def checkin_dia(request, dia_id):
    dia = get_object_or_404(DiaEvento, pk=dia_id)
    adolescentes = Adolescente.objects.all()
    filtro = request.GET.get('filtro', 'todos')  # padrão: todos

    presencas = Presenca.objects.filter(dia=dia)
    presentes_ids = presencas.filter(presente=True).values_list('adolescente_id', flat=True)

    # Aplica filtro
    if filtro == 'presentes':
        adolescentes = adolescentes.filter(id__in=presentes_ids)
    elif filtro == 'ausentes':
        adolescentes = adolescentes.exclude(id__in=presentes_ids)

    # Ordena: primeiro os presentes
    adolescentes = sorted(adolescentes, key=lambda x: x.id not in presentes_ids)

    if request.method == 'POST':
        presencas_ids = request.POST.getlist('presentes')
        Presenca.objects.filter(dia=dia).delete()
        for adol in adolescentes:
            Presenca.objects.create(
                adolescente=adol,
                dia=dia,
                presente=str(adol.id) in presencas_ids
            )
        messages.success(request, "Check-in realizado com sucesso!")
        return redirect('pagina_checkin')

    return render(request, 'checkin/checkin_dia.html', {
        'dia': dia,
        'adolescentes': adolescentes,
        'presentes_ids': presentes_ids,
        'filtro': filtro,
    })

@login_required
def adicionar_pg(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        lider = request.POST.get('lider')

        if nome:
            PequenoGrupo.objects.create(nome=nome, lider=lider)
            messages.success(request, "PG criado com sucesso.")
            return redirect('lista_pgs')
        else:
            messages.error(request, "O nome do PG é obrigatório.")

    return render(request, 'pgs/adicionar_pg.html')

@login_required
def lista_pgs(request):
    pgs = PequenoGrupo.objects.all()
    return render(request, 'pgs/lista_pgs.html', {'pgs': pgs})

@login_required
def detalhes_pg(request, pg_id):
    pg = get_object_or_404(PequenoGrupo, id=pg_id)
    adolescentes = Adolescente.objects.filter(pg=pg)
    return render(request, 'pgs/pg.html', {'pg': pg, 'adolescentes': adolescentes})
