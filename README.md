# Visor HTML interactivo para PowerPoint (Mac)

## 1. Alojar el complemento en GitHub Pages (una sola vez)
1. Crea una cuenta gratuita en github.com (si no la tienes).
2. Pulsa «New repository», llámalo exactamente `visor-html-ppt`, márcalo como Public y créalo.
3. En el repositorio: «Add file» > «Upload files». Arrastra `index.html` y la carpeta `assets`. Pulsa «Commit changes».
4. Settings > Pages > Source: «Deploy from a branch», Branch: `main`, carpeta `/ (root)`. Guardar.
5. En 1-2 minutos estará en `https://USUARIO.github.io/visor-html-ppt/` (USUARIO = tu nombre de GitHub).

## 2. Preparar el manifest
Abre `manifest.xml` con TextEdit y sustituye `USUARIO` por tu nombre de GitHub (aparece 5 veces). Guarda como texto sin formato.

## 3. Cargar el complemento en PowerPoint para Mac
1. Cierra PowerPoint.
2. En Finder: Ir > Ir a la carpeta… y pega:
   `~/Library/Containers/com.microsoft.Powerpoint/Data/Documents/wef`
   Si la carpeta `wef` no existe, créala dentro de `Documents`.
3. Copia ahí `manifest.xml`.
4. Abre PowerPoint con tu cuenta personal de Microsoft.
5. Insertar > Complementos > Mis complementos. Aparece «Visor HTML interactivo» (en la sección de complementos de desarrollador). Insértalo.

## 4. Usarlo
1. En la diapositiva, ajusta el tamaño del recuadro del complemento.
2. Pulsa ⚙ (abajo a la derecha) > «Archivo .html» > elige el HTML del artefacto > «Guardar y mostrar».
3. En modo presentación el botón ⚙ desaparece y el artefacto se maneja con el ratón como en la web.
4. Cada inserción del complemento guarda su propio HTML dentro del .pptx. Puedes poner uno en cada diapositiva.

## Notas
- Al abrir la presentación, PowerPoint descarga el complemento desde GitHub, así que necesita internet. El HTML ya va dentro del .pptx.
- El ordenador en el que presentes también tiene que tener el complemento cargado (pasos 3.1-3.5).
- Límite aproximado de 1,8 MB por HTML.
