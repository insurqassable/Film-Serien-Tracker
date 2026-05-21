# Relationsschema

**Haupttabellen**
<br>**User**: {PK user_id *int*; username *string*; password *string*}
<br>**FilmeSerien**: {PK filmserien_id *int*; fs_name *string*; typ *string*; tmdb_id *string*}
<br>**Genre**: {PK genre_id *int*; g_name *string*}

**Nebentabellen**
<br>**UserFilmeSerien**: {PK filmserien_id *int*; PK user_id *int*; listentyp *string*}
<br>**FilmeSerienGenre**: {PK filmserien_id *int*; PK genre_id *int*}
