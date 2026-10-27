
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from .models import Post


def lista_posts(request):
    posts = Post.objects.all()
    busqueda = request.GET.get('q', '')

    if busqueda:
        posts = posts.filter(
            Q(titulo__icontains=busqueda) |
            Q(contenido__icontains=busqueda)
        )

    return render(request, 'publicaciones/lista_posts.html', {
        'posts': posts,
        'busqueda': busqueda,
    })


def detalle_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'publicaciones/detalle_post.html', {
        'post': post,
    })


@login_required
def crear_post(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        imagen = request.FILES.get('imagen')

        if titulo and contenido:
            Post.objects.create(
                titulo=titulo,
                contenido=contenido,
                imagen=imagen,
                autor=request.user,
            )
            return redirect('lista_posts')

    return render(request, 'publicaciones/formulario_post.html')


@login_required
def editar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.autor != request.user and not request.user.is_staff:
        return redirect('detalle_post', pk=post.pk)

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        imagen = request.FILES.get('imagen')

        if titulo and contenido:
            post.titulo = titulo
            post.contenido = contenido

            if imagen:
                post.imagen = imagen

            post.save()
            return redirect('detalle_post', pk=post.pk)

    return render(request, 'publicaciones/formulario_post.html', {
        'post': post,
    })


@login_required
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.autor != request.user and not request.user.is_staff:
        return redirect('detalle_post', pk=post.pk)

    if request.method == 'POST':
        post.delete()
        return redirect('lista_posts')

    return render(request, 'publicaciones/confirmar_eliminacion.html', {
        'post': post,
    })


def registro(request):
    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            return redirect('lista_posts')
    else:
        formulario = UserCreationForm()

    return render(request, 'registration/registro.html', {
        'formulario': formulario,
    })
