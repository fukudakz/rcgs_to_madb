import os
import glob
import pandas as pd
from rdflib import Graph, Namespace
from rdflib.namespace import DC, DCTERMS, RDF, RDFS

def load_rdf_files(source_dir='./source'):
    """
    ./sourceディレクトリからすべてのRDFファイルを読み込み、統合したGraphを返す
    """
    merged_graph = Graph()
    
    # サポートするRDFファイル形式
    rdf_extensions = ['*.ttl', '*.rdf', '*.xml', '*.n3', '*.nt', '*.jsonld']
    
    total_files = 0
    loaded_files = 0
    
    print(f"RDFファイルの読み込みを開始: {source_dir}")
    
    for extension in rdf_extensions:
        pattern = os.path.join(source_dir, extension)
        files = glob.glob(pattern)
        total_files += len(files)
        
        for file_path in files:
            try:
                print(f"読み込み中: {file_path}")
                
                # ファイル拡張子に基づいてフォーマットを判定
                if file_path.endswith('.ttl'):
                    format_type = 'turtle'
                elif file_path.endswith('.rdf') or file_path.endswith('.xml'):
                    format_type = 'xml'
                elif file_path.endswith('.n3'):
                    format_type = 'n3'
                elif file_path.endswith('.nt'):
                    format_type = 'nt'
                elif file_path.endswith('.jsonld'):
                    format_type = 'json-ld'
                else:
                    format_type = 'turtle'  # デフォルト
                
                # ファイルを読み込み
                temp_graph = Graph()
                temp_graph.parse(file_path, format=format_type)
                
                # 統合グラフに追加
                merged_graph += temp_graph
                loaded_files += 1
                
                print(f"  成功: {len(temp_graph)} トリプルを読み込み")
                
            except Exception as e:
                print(f"  エラー: {file_path} - {str(e)}")
                continue
    
    print(f"\n読み込み完了:")
    print(f"  総ファイル数: {total_files}")
    print(f"  成功したファイル数: {loaded_files}")
    print(f"  統合グラフのトリプル数: {len(merged_graph)}")
    
    return merged_graph

def main():
    """
    メイン処理
    """
    # ./sourceディレクトリの存在確認
    if not os.path.exists('./source'):
        print("エラー: ./sourceディレクトリが見つかりません")
        return
    
    # RDFファイルの読み込み
    merged_graph = load_rdf_files('./source')
    
    if len(merged_graph) == 0:
        print("警告: 読み込まれたRDFデータがありません")
        return
    
    # 基本的な統計情報を表示
    print("\n=== データ統計 ===")
    
    # 名前空間の定義
    dcndl = Namespace("http://ndl.go.jp/dcndl/terms/")
    
    # BibResourceの数をカウント
    bib_resources = list(merged_graph.subjects(RDF.type, dcndl.BibResource))
    print(f"BibResource数: {len(bib_resources)}")
    
    # Itemの数をカウント
    items = list(merged_graph.subjects(RDF.type, dcndl.Item))
    print(f"Item数: {len(items)}")
    
    # 使用されている名前空間を表示
    print("\n使用されている名前空間:")
    for prefix, namespace in merged_graph.namespaces():
        print(f"  {prefix}: {namespace}")
    
    print("\nRDFファイルの読み込みが完了しました。")
    return merged_graph

def extract_game_package_data(merged_graph):
    """
    ゲームパッケージのデータを抽出してCSVに変換する
    """
    print("\n=== ゲームパッケージデータの抽出開始 ===")
    
    # 名前空間の定義
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    schema = Namespace("http://schema.org/")
    dcndl = Namespace("http://ndl.go.jp/dcndl/terms/")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    
    # rcgs:Packageタイプのリソースを取得
    package_resources = list(merged_graph.subjects(RDF.type, rcgs.Package))
    print(f"ゲームパッケージ数: {len(package_resources)}")
    
    if len(package_resources) == 0:
        print("警告: ゲームパッケージが見つかりませんでした")
        return None
    
    # データを格納するリスト
    package_data = []
    
    for i, resource in enumerate(package_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(package_resources)}")
        
        # 各プロパティを抽出
        row = {'resource_uri': str(resource)}
        
        # 基本プロパティ
        properties = {
            'schema_name': (schema.name, None),
            'schema_volumeNumber': (schema.volumeNumber, None),
            'schema_issueNumber': (schema.issueNumber, None),
            'schema_copyrightYear': (schema.copyrightYear, None),
            'dcndl_edition': (dcndl.edition, None),
            'dcndl_publicationPeriodicity': (dcndl.publicationPeriodicity, None),
            'dcndl_volume': (dcndl.volume, None),
            'dcterms_accessRights': (DCTERMS.accessRights, None),
            'dcterms_description': (DCTERMS.description, None),
            'dcterms_hasPart': (DCTERMS.hasPart, None),
            'dcterms_identifier': (DCTERMS.identifier, None),
            'dcterms_isPartOf': (DCTERMS.isPartOf, None),
            'dcterms_issued': (DCTERMS.issued, None),
            'dcterms_rights': (DCTERMS.rights, None),
            'dcterms_tableOfContents': (DCTERMS.tableOfContents, None),
            'dcterms_medium': (DCTERMS.medium, None),
            'rcgs_abbreviatedTitle': (rcgs.abbreviatedTitle, None),
            'rcgs_digitalFileType': (rcgs.digitalFileType, None),
            'rcgs_distributor': (rcgs.distributor, None),
            'rcgs_jpNumber': (rcgs.jpNumber, None),
            'rcgs_manufacturer': (rcgs.manufacturer, None),
            'rcgs_middlewareOrGameEngine': (rcgs.middlewareOrGameEngine, None),
            'rcgs_modelNumber': (rcgs.modelNumber, None),
            'rcgs_modeOfIssuance': (rcgs.modeOfIssuance, None),
            'rcgs_ndlBibID': (rcgs.ndlBibID, None),
            'rcgs_oclcNumber': (rcgs.oclcNumber, None),
            'rcgs_parallelTitle': (rcgs.parallelTitle, None),
            'rcgs_producer': (rcgs.producer, None),
            'rcgs_publisher': (rcgs.publisher, None),
            'rcgs_ratingContentDescriptor': (rcgs.ratingContentDescriptor, None),
            'rcgs_representativeImage': (rcgs.representativeImage, None),
            'rcgs_responsibilityStatement': (rcgs.responsibilityStatement, None),
            'rcgs_seriesStatement': (rcgs.seriesStatement, None),
            'rcgs_subseriesStatement': (rcgs.subseriesStatement, None),
            'rcgs_variantTitle': (rcgs.variantTitle, None),
            'rcgs_dimension': (rcgs.dimension, None),
            'schema_brand': (schema.brand, None),
            'schema_contactPoints': (schema.contactPoints, None),
            'schema_contentRating': (schema.contentRating, None),
            'schema_gamePlatform': (schema.gamePlatform, None),
            'schema_gtin13': (schema.gtin13, None),
            'schema_isbn': (schema.isbn, None),
            'schema_issn': (schema.issn, None),
            'schema_numberOfPlayers': (schema.numberOfPlayers, None),
            'schema_price': (schema.price, None),
            'schema_requirement': (schema.requirement, None),
            'schema_serialNumber': (schema.serialNumber, None),
            'schema_thumbnailUrl': (schema.thumbnailUrl, None),
            'schema_url': (schema.url, None),
            'schema_videoFrameSize': (schema.videoFrameSize, None),
            'rdf_type': (RDF.type, None)
        }
        
        # 各プロパティの値を抽出
        for field_name, (property_uri, lang_filter) in properties.items():
            values = []
            for obj in merged_graph.objects(resource, property_uri):
                if lang_filter:
                    # 言語フィルターがある場合
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        # 特殊なプロパティ（複雑な構造）
        # dcndl:titleTranscription (言語別)
        ja_hrkt_values = []
        ja_latn_values = []
        for obj in merged_graph.objects(resource, dcndl.titleTranscription):
            if hasattr(obj, 'language'):
                if obj.language == 'ja-Hrkt':
                    ja_hrkt_values.append(str(obj))
                elif obj.language == 'ja-Latn':
                    ja_latn_values.append(str(obj))
        row['dcndl_titleTranscription_jaHrkt'] = "|".join(ja_hrkt_values)
        row['dcndl_titleTranscription_jaLatn'] = "|".join(ja_latn_values)
        
        # dcterms:format (複雑な構造)
        format_labels = []
        format_carrier_types = []
        format_extents = []
        format_encoding_formats = []
        format_dimensions = []
        format_file_sizes = []
        format_descriptions = []
        format_notes = []
        
        for format_node in merged_graph.objects(resource, DCTERMS.format):
            for label in merged_graph.objects(format_node, RDFS.label):
                format_labels.append(str(label))
            for carrier_type in merged_graph.objects(format_node, rcgs.carrierType):
                format_carrier_types.append(str(carrier_type))
            for extent in merged_graph.objects(format_node, DCTERMS.extent):
                format_extents.append(str(extent))
            for encoding_format in merged_graph.objects(format_node, schema.encodingFormat):
                format_encoding_formats.append(str(encoding_format))
            for dimension in merged_graph.objects(format_node, rcgs.dimension):
                format_dimensions.append(str(dimension))
            for file_size in merged_graph.objects(format_node, schema.fileSize):
                format_file_sizes.append(str(file_size))
            for description in merged_graph.objects(format_node, DCTERMS.description):
                format_descriptions.append(str(description))
            for note in merged_graph.objects(format_node, skos.note):
                format_notes.append(str(note))
        
        row['format_rdfs_label'] = "|".join(format_labels)
        row['format_rcgs_carrierType'] = "|".join(format_carrier_types)
        row['format_dcterms_extent'] = "|".join(format_extents)
        row['format_schema_encodingFormat'] = "|".join(format_encoding_formats)
        row['format_rcgs_dimension'] = "|".join(format_dimensions)
        row['format_schema_fileSize'] = "|".join(format_file_sizes)
        row['format_dcterms_description'] = "|".join(format_descriptions)
        row['format_skos_note'] = "|".join(format_notes)
        
        # rcgs:formatOfSubunit (複雑な構造)
        subunit_labels = []
        subunit_carrier_types = []
        subunit_extents = []
        subunit_encoding_formats = []
        subunit_dimensions = []
        subunit_file_sizes = []
        subunit_descriptions = []
        subunit_notes = []
        
        for subunit_node in merged_graph.objects(resource, rcgs.formatOfSubunit):
            for label in merged_graph.objects(subunit_node, RDFS.label):
                subunit_labels.append(str(label))
            for carrier_type in merged_graph.objects(subunit_node, rcgs.carrierType):
                subunit_carrier_types.append(str(carrier_type))
            for extent in merged_graph.objects(subunit_node, DCTERMS.extent):
                subunit_extents.append(str(extent))
            for encoding_format in merged_graph.objects(subunit_node, schema.encodingFormat):
                subunit_encoding_formats.append(str(encoding_format))
            for dimension in merged_graph.objects(subunit_node, rcgs.dimension):
                subunit_dimensions.append(str(dimension))
            for file_size in merged_graph.objects(subunit_node, schema.fileSize):
                subunit_file_sizes.append(str(file_size))
            for description in merged_graph.objects(subunit_node, DCTERMS.description):
                subunit_descriptions.append(str(description))
            for note in merged_graph.objects(subunit_node, skos.note):
                subunit_notes.append(str(note))
        
        row['subunit_rdfs_label'] = "|".join(subunit_labels)
        row['subunit_rcgs_carrierType'] = "|".join(subunit_carrier_types)
        row['subunit_dcterms_extent'] = "|".join(subunit_extents)
        row['subunit_schema_encodingFormat'] = "|".join(subunit_encoding_formats)
        row['subunit_rcgs_dimension'] = "|".join(subunit_dimensions)
        row['subunit_schema_fileSize'] = "|".join(subunit_file_sizes)
        row['subunit_dcterms_description'] = "|".join(subunit_descriptions)
        row['subunit_skos_note'] = "|".join(subunit_notes)
        
        # rcgs:provisionActivity (複雑な構造)
        pa_types = []
        pa_publisher_statements = []
        pa_dates = []
        pa_spatials = []
        pa_sources = []
        pa_notes = []
        
        for pa_node in merged_graph.objects(resource, rcgs.provisionActivity):
            for pa_type in merged_graph.objects(pa_node, RDF.type):
                pa_types.append(str(pa_type))
            for publisher_statement in merged_graph.objects(pa_node, rcgs.publisherStatement):
                pa_publisher_statements.append(str(publisher_statement))
            for date in merged_graph.objects(pa_node, DCTERMS.date):
                pa_dates.append(str(date))
            for spatial in merged_graph.objects(pa_node, DCTERMS.spatial):
                pa_spatials.append(str(spatial))
            for source in merged_graph.objects(pa_node, DCTERMS.source):
                pa_sources.append(str(source))
            for note in merged_graph.objects(pa_node, skos.note):
                pa_notes.append(str(note))
        
        row['PA_rdf_type'] = "|".join(pa_types)
        row['PA_rcgs_publisherStatement'] = "|".join(pa_publisher_statements)
        row['PA_dcterms_date'] = "|".join(pa_dates)
        row['PA_dcterms_spatial'] = "|".join(pa_spatials)
        row['PA_dcterms_source'] = "|".join(pa_sources)
        row['PA_skos_note'] = "|".join(pa_notes)
        
        package_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(package_data)
    
    print(f"抽出完了: {len(df)} 件のゲームパッケージデータ")
    print(f"列数: {len(df.columns)}")
    
    return df

def extract_item_data(merged_graph):
    """
    個別資料（Item）のデータを抽出してCSVに変換する
    """
    print("\n=== 個別資料データの抽出開始 ===")
    
    # 名前空間の定義
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    schema = Namespace("http://schema.org/")
    dcndl = Namespace("http://ndl.go.jp/dcndl/terms/")
    
    # rcgs:Itemタイプのリソースを取得
    item_resources = list(merged_graph.subjects(RDF.type, rcgs.Item))
    print(f"個別資料数: {len(item_resources)}")
    
    if len(item_resources) == 0:
        print("警告: 個別資料が見つかりませんでした")
        return None
    
    # データを格納するリスト
    item_data = []
    
    for i, resource in enumerate(item_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(item_resources)}")
        
        # 各プロパティを抽出
        row = {'resource_uri': str(resource)}
        
        # rcgs:exemplarOfを確認（Packageへの参照）
        exemplar_of = list(merged_graph.objects(resource, rcgs.exemplarOf))
        if exemplar_of:
            # exemplarOfがPackageタイプかチェック
            for exemplar in exemplar_of:
                if (exemplar, RDF.type, rcgs.Package) in merged_graph:
                    row['exemplarOf'] = str(exemplar)
                    break
            else:
                row['exemplarOf'] = ""
        else:
            row['exemplarOf'] = ""
        
        # 基本プロパティ
        properties = {
            'identifier': (DCTERMS.identifier, None),
            'spatial': (DCTERMS.spatial, None),
            'owns': (schema.owns, None),
            'holdingAgent': (dcndl.holdlingAgent, None)
        }
        
        # 各プロパティの値を抽出
        for field_name, (property_uri, lang_filter) in properties.items():
            values = []
            for obj in merged_graph.objects(resource, property_uri):
                if lang_filter:
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        item_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(item_data)
    
    print(f"抽出完了: {len(df)} 件の個別資料データ")
    print(f"列数: {len(df.columns)}")
    
    return df

def extract_person_data(merged_graph):
    """
    個人（Person）のデータを抽出してCSVに変換する
    """
    print("\n=== 個人データの抽出開始 ===")
    
    # 名前空間の定義
    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    schema = Namespace("http://schema.org/")
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    
    # foaf:Personタイプのリソースを取得
    person_resources = list(merged_graph.subjects(RDF.type, foaf.Person))
    print(f"個人数: {len(person_resources)}")
    
    if len(person_resources) == 0:
        print("警告: 個人が見つかりませんでした")
        return None
    
    # データを格納するリスト
    person_data = []
    
    for i, resource in enumerate(person_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(person_resources)}")
        
        # 各プロパティを抽出
        row = {'resource_uri': str(resource)}
        
        # 基本プロパティ（言語別）
        ja_pref_labels = []
        en_pref_labels = []
        for obj in merged_graph.objects(resource, skos.prefLabel):
            if hasattr(obj, 'language'):
                if obj.language == 'ja':
                    ja_pref_labels.append(str(obj))
                elif obj.language == 'en':
                    en_pref_labels.append(str(obj))
        row['prefLabel_ja'] = "|".join(ja_pref_labels)
        row['prefLabel_en'] = "|".join(en_pref_labels)
        
        # その他のプロパティ
        properties = {
            'altLabel': (skos.altLabel, None),
            'homepage': (foaf.homepage, None),
            'description': (DCTERMS.description, None),
            'identifier': (DCTERMS.identifier, None),
            'ndlAuthoritiesID': (rcgs.ndlAuthoritiesID, None),
            'viafID': (rcgs.viafID, None),
            'wikidataID': (rcgs.wikidataID, None),
            'twitterID': (rcgs.twitterID, None),
            'seeAlso': (RDFS.seeAlso, None),
            'language': (DCTERMS.language, None),
            'disambiguatingDescription': (schema.disambiguatingDescription, None),
            'note': (skos.note, None),
            'hasOccupation': (schema.hasOccupation, None),
            'birthDate': (schema.birthDate, None),
            'deathDate': (schema.deathDate, None),
            'birthPlace': (schema.birthPlace, None),
            'deathPlace': (schema.deathPlace, None),
            'homeLocation': (schema.homeLocation, None),
            'mbox': (foaf.mbox, None),
            'addressCountry': (schema.addressCountry, None),
            'additionalName': (schema.additionalName, None),
            'title': (foaf.title, None)
        }
        
        # 各プロパティの値を抽出
        for field_name, (property_uri, lang_filter) in properties.items():
            values = []
            for obj in merged_graph.objects(resource, property_uri):
                if lang_filter:
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        # rcgs:adminMetadataからのsource
        source_values = []
        for admin_meta in merged_graph.objects(resource, rcgs.adminMetadata):
            for source in merged_graph.objects(admin_meta, DCTERMS.source):
                source_values.append(str(source))
        row['source'] = "|".join(source_values)
        
        person_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(person_data)
    
    print(f"抽出完了: {len(df)} 件の個人データ")
    print(f"列数: {len(df.columns)}")
    
    return df

def extract_organization_data(merged_graph):
    """
    団体（Organization）のデータを抽出してCSVに変換する
    """
    print("\n=== 団体データの抽出開始 ===")
    
    # 名前空間の定義
    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    schema = Namespace("http://schema.org/")
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    
    # foaf:Organizationタイプのリソースを取得
    org_resources = list(merged_graph.subjects(RDF.type, foaf.Organization))
    print(f"団体数: {len(org_resources)}")
    
    if len(org_resources) == 0:
        print("警告: 団体が見つかりませんでした")
        return None
    
    # データを格納するリスト
    org_data = []
    
    for i, resource in enumerate(org_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(org_resources)}")
        
        # 各プロパティを抽出
        row = {'resource_uri': str(resource)}
        
        # 基本プロパティ（言語別）
        ja_pref_labels = []
        en_pref_labels = []
        for obj in merged_graph.objects(resource, skos.prefLabel):
            if hasattr(obj, 'language'):
                if obj.language == 'ja':
                    ja_pref_labels.append(str(obj))
                elif obj.language == 'en':
                    en_pref_labels.append(str(obj))
        row['skos_prefLabel_ja'] = "|".join(ja_pref_labels)
        row['skos_prefLabel_en'] = "|".join(en_pref_labels)
        
        # その他のプロパティ
        properties = {
            'altLabel': (skos.altLabel, None),
            'homepage': (foaf.homepage, None),
            'description': (DCTERMS.description, None),
            'identifier': (DCTERMS.identifier, None),
            'ndlAuthoritiesID': (rcgs.ndlAuthoritiesID, None),
            'viafID': (rcgs.viafID, None),
            'wikidataID': (rcgs.wikidataID, None),
            'twitterID': (rcgs.twitterID, None),
            'seeAlso': (RDFS.seeAlso, None),
            'language': (DCTERMS.language, None),
            'disambiguatingDescription': (schema.disambiguatingDescription, None),
            'note': (skos.note, None),
            'additionalType': (schema.additionalType, None),
            'startDate': (schema.startDate, None),
            'endDate': (schema.endDate, None),
            'address': (schema.address, None),
            'latitude': (schema.latitude, None),
            'longitude': (schema.longitude, None),
            'relatedOrganization': (rcgs.relatedOrganization, None),
            'member': (foaf.member, None),
            'logo': (foaf.logo, None)
        }
        
        # 各プロパティの値を抽出
        for field_name, (property_uri, lang_filter) in properties.items():
            values = []
            for obj in merged_graph.objects(resource, property_uri):
                if lang_filter:
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        # rcgs:adminMetadataからのsource
        source_values = []
        for admin_meta in merged_graph.objects(resource, rcgs.adminMetadata):
            for source in merged_graph.objects(admin_meta, DCTERMS.source):
                source_values.append(str(source))
        row['source'] = "|".join(source_values)
        
        org_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(org_data)
    
    print(f"抽出完了: {len(df)} 件の団体データ")
    print(f"列数: {len(df.columns)}")
    
    return df

def extract_variation_data(merged_graph):
    """
    バリエーション（Variation）のデータを抽出してCSVに変換する
    """
    print("\n=== バリエーションデータの抽出開始 ===")
    
    # 名前空間の定義
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    schema = Namespace("http://schema.org/")
    
    # rcgs:Variationタイプのリソースを取得
    variation_resources = list(merged_graph.subjects(RDF.type, rcgs.Variation))
    print(f"バリエーション数: {len(variation_resources)}")
    
    if len(variation_resources) == 0:
        print("警告: バリエーションが見つかりませんでした")
        return None
    
    # データを格納するリスト
    variation_data = []
    
    for i, resource in enumerate(variation_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(variation_resources)}")
        
        # 各プロパティを抽出
        row = {'resource_uri': str(resource)}
        
        # 基本プロパティ
        properties = {
            'contribution': (rcgs.contribution, None),
            'contentType': (rcgs.contentType, None),
            'variationOf': (rcgs.variationOf, None),
            'type': (RDF.type, None),
            'label': (RDFS.label, None),
            'color': (schema.color, None),
            'audio': (schema.audio, None),
            'language': (DCTERMS.language, None),
            'date': (DCTERMS.date, None),
            'gamePlatform': (schema.gamePlatform, None),
            'aspectRatio': (rcgs.aspectRatio, None),
            'middlewareOrGameEngine': (rcgs.middlewareOrGameEngine, None),
            'dimension': (rcgs.dimension, None),
            'pointOfView': (rcgs.pointOfView, None),
            'ending': (rcgs.ending, None),
            'multipleEnding': (rcgs.multipleEnding, None),
            'disambiguatingDescription': (schema.disambiguatingDescription, None),
            'difficultyOption': (rcgs.difficultyOption, None),
            'award': (schema.award, None),
            'abstract': (DCTERMS.abstract, None),
            'postGameContents': (rcgs.postGameContents, None)
        }
        
        # 各プロパティの値を抽出
        for field_name, (property_uri, lang_filter) in properties.items():
            values = []
            for obj in merged_graph.objects(resource, property_uri):
                if lang_filter:
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        variation_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(variation_data)
    
    print(f"抽出完了: {len(df)} 件のバリエーションデータ")
    print(f"列数: {len(df.columns)}")
    
    return df

def extract_work_data(merged_graph):
    """
    作品（Work）のデータを抽出してCSVに変換する
    """
    print("\n=== 作品データの抽出開始 ===")
    
    # 名前空間の定義
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    schema = Namespace("http://schema.org/")
    
    # rcgs:Workタイプのリソースを取得
    work_resources = list(merged_graph.subjects(RDF.type, rcgs.Work))
    print(f"作品数: {len(work_resources)}")
    
    if len(work_resources) == 0:
        print("警告: 作品が見つかりませんでした")
        return None
    
    # データを格納するリスト
    work_data = []
    
    for i, resource in enumerate(work_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(work_resources)}")
        
        # 各プロパティを抽出
        row = {'resource_uri': str(resource)}
        
        # 基本プロパティ
        properties = {
            'label': (RDFS.label, None),
            'prefLabel': (skos.prefLabel, None),
            'altLabel': (skos.altLabel, None),
            'spatial': (DCTERMS.spatial, None),
            'date': (DCTERMS.date, None),
            'description': (DCTERMS.description, None),
            'identifier': (DCTERMS.identifier, None),
            'closeMatch': (skos.closeMatch, None),
            'twitch': (rcgs.twitch, None),
            'freebase': (rcgs.freebase, None),
            'mobyGames': (rcgs.mobyGames, None),
            'metacritic': (rcgs.metacritic, None),
            'seeAlso': (RDFS.seeAlso, None),
            'imdb': (rcgs.imdb, None),
            'abstract': (DCTERMS.abstract, None),
            'audience': (DCTERMS.audience, None),
            'natureOfContent': (rcgs.natureOfContent, None),
            'serialNumber': (schema.serialNumber, None),
            'disambiguatingDescription': (schema.disambiguatingDescription, None),
            'locationCreated': (schema.locationCreated, None),
            'about': (schema.about, None),
            'subjectOf': (schema.subjectOf, None),
            'gameLocation': (schema.gameLocation, None),
            'creator': (DCTERMS.creator, None),
            'productionCompany': (schema.productionCompany, None),
            'relatedAgent': (rcgs.relatedAgent, None),
            'logo': (schema.logo, None),
            'relation': (DCTERMS.relation, None),
            'isPartOf': (DCTERMS.isPartOf, None),
            'hasPart': (DCTERMS.hasPart, None),
            'precedes': (rcgs.precedes, None),
            'succeeds': (rcgs.succeeds, None),
            'sequelTo': (rcgs.sequelTo, None),
            'sequel': (rcgs.sequel, None),
            'remadeAs': (rcgs.remadeAs, None),
            'complements': (rcgs.complements, None),
            'expandedAs': (rcgs.expandedAs, None),
            'spinOff': (rcgs.spinOff, None),
            'note': (skos.note, None)
        }
        
        # 各プロパティの値を抽出
        for field_name, (property_uri, lang_filter) in properties.items():
            values = []
            for obj in merged_graph.objects(resource, property_uri):
                if lang_filter:
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        # 複雑な構造（rdfs:labelを持つリソース）
        # schema:genre
        genre_labels = []
        for genre_node in merged_graph.objects(resource, schema.genre):
            for label in merged_graph.objects(genre_node, RDFS.label):
                genre_labels.append(str(label))
        row['genre'] = "|".join(genre_labels)
        
        # rcgs:narrativeGenre
        narrative_genre_labels = []
        for ng_node in merged_graph.objects(resource, rcgs.narrativeGenre):
            for label in merged_graph.objects(ng_node, RDFS.label):
                narrative_genre_labels.append(str(label))
        row['narrativeGenre'] = "|".join(narrative_genre_labels)
        
        # rcgs:theme
        theme_labels = []
        for theme_node in merged_graph.objects(resource, rcgs.theme):
            for label in merged_graph.objects(theme_node, RDFS.label):
                theme_labels.append(str(label))
        row['theme'] = "|".join(theme_labels)
        
        # rcgs:mood
        mood_labels = []
        for mood_node in merged_graph.objects(resource, rcgs.mood):
            for label in merged_graph.objects(mood_node, RDFS.label):
                mood_labels.append(str(label))
        row['mood'] = "|".join(mood_labels)
        
        # rcgs:setting
        setting_labels = []
        for setting_node in merged_graph.objects(resource, rcgs.setting):
            for label in merged_graph.objects(setting_node, RDFS.label):
                setting_labels.append(str(label))
        row['setting'] = "|".join(setting_labels)
        
        # rcgs:series
        series_labels = []
        for series_node in merged_graph.objects(resource, rcgs.series):
            for label in merged_graph.objects(series_node, RDFS.label):
                series_labels.append(str(label))
        row['series'] = "|".join(series_labels)
        
        # rcgs:franchise
        franchise_labels = []
        for franchise_node in merged_graph.objects(resource, rcgs.franchise):
            for label in merged_graph.objects(franchise_node, RDFS.label):
                franchise_labels.append(str(label))
        row['franchise'] = "|".join(franchise_labels)
        
        # rcgs:mechanic
        mechanic_labels = []
        for mechanic_node in merged_graph.objects(resource, rcgs.mechanic):
            for label in merged_graph.objects(mechanic_node, RDFS.label):
                mechanic_labels.append(str(label))
        row['mechanic'] = "|".join(mechanic_labels)
        
        # rcgs:protagonist
        protagonist_labels = []
        for protagonist_node in merged_graph.objects(resource, rcgs.protagonist):
            for label in merged_graph.objects(protagonist_node, RDFS.label):
                protagonist_labels.append(str(label))
        row['protagonist'] = "|".join(protagonist_labels)
        
        work_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(work_data)
    
    print(f"抽出完了: {len(df)} 件の作品データ")
    print(f"列数: {len(df.columns)}")
    
    return df

def extract_related_item_data(merged_graph):
    """
    関連資料（Item）のデータを抽出してCSVに変換する
    """
    print("\n=== 関連資料データの抽出開始 ===")
    
    # 名前空間の定義
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    schema = Namespace("http://schema.org/")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    dcndl = Namespace("http://ndl.go.jp/dcndl/terms/")
    
    # rcgs:Itemタイプのリソースを取得（exemplarOfを持つもの）
    item_resources = []
    for item in merged_graph.subjects(RDF.type, rcgs.Item):
        exemplar_of = list(merged_graph.objects(item, rcgs.exemplarOf))
        if exemplar_of:
            item_resources.append(item)
    
    print(f"関連資料数: {len(item_resources)}")
    
    if len(item_resources) == 0:
        print("警告: 関連資料が見つかりませんでした")
        return None
    
    # データを格納するリスト
    related_item_data = []
    
    for i, item_resource in enumerate(item_resources):
        if i % 100 == 0:
            print(f"処理中: {i+1}/{len(item_resources)}")
        
        # 各プロパティを抽出
        row = {'item_uri': str(item_resource)}
        
        # Itemの基本プロパティ
        item_properties = {
            'item_holdingAgent': (dcndl.holdlingAgent, None),
            'item_identifier': (DCTERMS.identifier, None),
            'item_spatial': (DCTERMS.spatial, None),
            'item_owns': (schema.owns, None)
        }
        
        for field_name, (property_uri, lang_filter) in item_properties.items():
            values = []
            for obj in merged_graph.objects(item_resource, property_uri):
                if lang_filter:
                    if hasattr(obj, 'language') and obj.language == lang_filter:
                        values.append(str(obj))
                else:
                    values.append(str(obj))
            row[field_name] = "|".join(values) if values else ""
        
        # exemplarOfからPackageリソースを取得
        exemplar_of = list(merged_graph.objects(item_resource, rcgs.exemplarOf))
        if exemplar_of:
            package_resource = exemplar_of[0]
            row['exemplarOf'] = str(package_resource)
            
            # Packageの基本プロパティ
            properties = {
                'type': (RDF.type, None),
                'name': (schema.name, None),
                'parallelTitle': (rcgs.parallelTitle, None),
                'alternative': (DCTERMS.alternative, None),
                'abbreviatedTitle': (rcgs.abbreviatedTitle, None),
                'edition': (dcndl.edition, None),
                'volume': (dcndl.volume, None),
                'responsibilityStatement': (rcgs.responsibilityStatement, None),
                'creator': (DCTERMS.creator, None),
                'contribution': (rcgs.contribution, None),
                'issued': (DCTERMS.issued, None),
                'dimension': (rcgs.dimension, None),
                'medium': (DCTERMS.medium, None),
                'identifier': (DCTERMS.identifier, None),
                'gtin13': (schema.gtin13, None),
                'isbn': (schema.isbn, None),
                'issn': (schema.issn, None),
                'modelNumber': (rcgs.modelNumber, None),
                'jpNumber': (rcgs.jpNumber, None),
                'ndlBiBID': (rcgs.ndlBiBID, None),
                'oclcNumber': (rcgs.oclcNumber, None),
                'seeAlso': (RDFS.seeAlso, None),
                'copyrightYear': (schema.copyrightYear, None),
                'accessRights': (DCTERMS.accessRights, None),
                'hasPart': (DCTERMS.hasPart, None),
                'isPartOf': (DCTERMS.isPartOf, None),
                'abstract': (DCTERMS.abstract, None),
                'description': (DCTERMS.description, None),
                'relation': (DCTERMS.relation, None),
                'references': (DCTERMS.references, None),
                'isReferencedBy': (DCTERMS.isReferencedBy, None),
                'language': (DCTERMS.language, None),
                'about': (schema.about, None),
                'subjectOf': (schema.subjectOf, None),
                'tableOfContents': (DCTERMS.tableOfContents, None),
                'brand': (schema.brand, None),
                'producer': (rcgs.producer, None),
                'publisher': (rcgs.publisher, None),
                'distributor': (rcgs.distributor, None),
                'manufacturer': (rcgs.manufacturer, None),
                'seriesStatement': (rcgs.seriesStatement, None),
                'subseriesStatement': (rcgs.subseriesStatement, None),
                'modeOfIssuance': (rcgs.modeOfIssuance, None),
                'publicationPeriodicity': (dcndl.publicationPeriodicity, None),
                'serialNumber': (schema.serialNumber, None),
                'volumeNumber': (schema.volumeNumber, None),
                'issueNumber': (schema.issueNumber, None),
                'price': (schema.price, None),
                'exemplar': (rcgs.exemplar, None),
                'downloadUrl': (schema.downloadUrl, None),
                'created': (DCTERMS.created, None),
                'locationCreated': (schema.locationCreated, None),
                'thumbnailUrl': (schema.thumbnailUrl, None),
                'source': (DCTERMS.source, None)
            }
            
            # 各プロパティの値を抽出
            for field_name, (property_uri, lang_filter) in properties.items():
                values = []
                for obj in merged_graph.objects(package_resource, property_uri):
                    if lang_filter:
                        if hasattr(obj, 'language') and obj.language == lang_filter:
                            values.append(str(obj))
                    else:
                        values.append(str(obj))
                row[field_name] = "|".join(values) if values else ""
            
            # 特殊なプロパティ（言語別）
            # dcndl:titleTranscription
            ja_hrkt_values = []
            ja_latn_values = []
            for obj in merged_graph.objects(package_resource, dcndl.titleTranscription):
                if hasattr(obj, 'language'):
                    if obj.language == 'ja-Hrkt':
                        ja_hrkt_values.append(str(obj))
                    elif obj.language == 'ja-Latn':
                        ja_latn_values.append(str(obj))
            row['titleTranscription_jaHrkt'] = "|".join(ja_hrkt_values)
            row['titleTranscription_jaLatn'] = "|".join(ja_latn_values)
            
            # 複雑な構造
            # dcterms:format
            format_carrier_types = []
            format_extents = []
            format_dimensions = []
            format_encoding_formats = []
            format_content_sizes = []
            format_sources = []
            
            for format_node in merged_graph.objects(package_resource, DCTERMS.format):
                for carrier_type in merged_graph.objects(format_node, rcgs.carrierType):
                    format_carrier_types.append(str(carrier_type))
                for extent in merged_graph.objects(format_node, DCTERMS.extent):
                    format_extents.append(str(extent))
                for dimension in merged_graph.objects(format_node, rcgs.dimension):
                    format_dimensions.append(str(dimension))
                for encoding_format in merged_graph.objects(format_node, schema.encodingFormat):
                    format_encoding_formats.append(str(encoding_format))
                for content_size in merged_graph.objects(format_node, schema.contentSize):
                    format_content_sizes.append(str(content_size))
                for admin_meta in merged_graph.objects(format_node, rcgs.adminMetadata):
                    for source in merged_graph.objects(admin_meta, DCTERMS.source):
                        format_sources.append(str(source))
            
            row['format_carrierType'] = "|".join(format_carrier_types)
            row['format_extent'] = "|".join(format_extents)
            row['format_dimension'] = "|".join(format_dimensions)
            row['format_encodingFormat'] = "|".join(format_encoding_formats)
            row['format_contentSize'] = "|".join(format_content_sizes)
            row['format_source'] = "|".join(format_sources)
            
            # rcgs:formatOfSubunit
            subunit_carrier_types = []
            subunit_extents = []
            subunit_dimensions = []
            subunit_encoding_formats = []
            subunit_content_sizes = []
            subunit_sources = []
            
            for subunit_node in merged_graph.objects(package_resource, rcgs.formatOfSubunit):
                for carrier_type in merged_graph.objects(subunit_node, rcgs.carrierType):
                    subunit_carrier_types.append(str(carrier_type))
                for extent in merged_graph.objects(subunit_node, DCTERMS.extent):
                    subunit_extents.append(str(extent))
                for dimension in merged_graph.objects(subunit_node, rcgs.dimension):
                    subunit_dimensions.append(str(dimension))
                for encoding_format in merged_graph.objects(subunit_node, schema.encodingFormat):
                    subunit_encoding_formats.append(str(encoding_format))
                for content_size in merged_graph.objects(subunit_node, schema.contentSize):
                    subunit_content_sizes.append(str(content_size))
                for admin_meta in merged_graph.objects(subunit_node, rcgs.adminMetadata):
                    for source in merged_graph.objects(admin_meta, DCTERMS.source):
                        subunit_sources.append(str(source))
            
            row['subunit_carrierType'] = "|".join(subunit_carrier_types)
            row['subunit_extent'] = "|".join(subunit_extents)
            row['subunit_dimension'] = "|".join(subunit_dimensions)
            row['subunit_encodingFormat'] = "|".join(subunit_encoding_formats)
            row['subunit_contentSize'] = "|".join(subunit_content_sizes)
            row['subunit_source'] = "|".join(subunit_sources)
            
            # rcgs:provisionActivity
            pa_types = []
            pa_publisher_statements = []
            pa_dates = []
            pa_spatials = []
            pa_sources = []
            pa_notes = []
            
            for pa_node in merged_graph.objects(package_resource, rcgs.provisionActivity):
                for pa_type in merged_graph.objects(pa_node, RDF.type):
                    pa_types.append(str(pa_type))
                for publisher_statement in merged_graph.objects(pa_node, rcgs.publisherStatement):
                    pa_publisher_statements.append(str(publisher_statement))
                for date in merged_graph.objects(pa_node, DCTERMS.date):
                    pa_dates.append(str(date))
                for spatial in merged_graph.objects(pa_node, DCTERMS.spatial):
                    pa_spatials.append(str(spatial))
                for source in merged_graph.objects(pa_node, DCTERMS.source):
                    pa_sources.append(str(source))
                for note in merged_graph.objects(pa_node, skos.note):
                    pa_notes.append(str(note))
            
            row['PA_type'] = "|".join(pa_types)
            row['PA_publisherStatement'] = "|".join(pa_publisher_statements)
            row['PA_date'] = "|".join(pa_dates)
            row['PA_spatial'] = "|".join(pa_spatials)
            row['PA_source'] = "|".join(pa_sources)
            row['PA_note'] = "|".join(pa_notes)
            
            # rcgs:adminMetadataからのsource
            admin_source_values = []
            for admin_meta in merged_graph.objects(package_resource, rcgs.adminMetadata):
                for source in merged_graph.objects(admin_meta, DCTERMS.source):
                    admin_source_values.append(str(source))
            row['admin_source'] = "|".join(admin_source_values)
        else:
            row['exemplarOf'] = ""
            # 空の値を設定
            for field in ['type', 'name', 'titleTranscription_jaHrkt', 'titleTranscription_jaLatn', 
                         'parallelTitle', 'alternative', 'abbreviatedTitle', 'edition', 'volume',
                         'responsibilityStatement', 'creator', 'contribution', 'issued',
                         'format_carrierType', 'format_extent', 'format_dimension', 'format_encodingFormat',
                         'format_contentSize', 'format_source', 'subunit_carrierType', 'subunit_extent',
                         'subunit_dimension', 'subunit_encodingFormat', 'subunit_contentSize', 'subunit_source',
                         'dimension', 'medium', 'identifier', 'gtin13', 'isbn', 'issn', 'modelNumber',
                         'jpNumber', 'ndlBiBID', 'oclcNumber', 'seeAlso', 'copyrightYear', 'accessRights',
                         'hasPart', 'isPartOf', 'abstract', 'description', 'relation', 'references',
                         'isReferencedBy', 'language', 'about', 'subjectOf', 'tableOfContents', 'brand',
                         'PA_type', 'PA_publisherStatement', 'PA_date', 'PA_spatial', 'PA_source', 'PA_note',
                         'producer', 'publisher', 'distributor', 'manufacturer', 'seriesStatement',
                         'subseriesStatement', 'modeOfIssuance', 'publicationPeriodicity', 'serialNumber',
                         'volumeNumber', 'issueNumber', 'price', 'exemplar', 'downloadUrl', 'created',
                         'locationCreated', 'thumbnailUrl', 'source', 'admin_source']:
                row[field] = ""
        
        related_item_data.append(row)
    
    # DataFrameに変換
    df = pd.DataFrame(related_item_data)
    
    print(f"抽出完了: {len(df)} 件の関連資料データ")
    print(f"列数: {len(df.columns)}")
    
    return df

def save_to_csv(df, filename, output_dir='./output'):
    """
    DataFrameをCSVファイルに保存
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"出力ディレクトリを作成: {output_dir}")
    
    output_file = os.path.join(output_dir, filename)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"CSVファイルを保存: {output_file}")
    
    # 基本統計情報を表示
    print(f"  行数: {len(df)}")
    print(f"  列数: {len(df.columns)}")
    print(f"  ファイルサイズ: {os.path.getsize(output_file) / 1024:.1f} KB")

def main():
    """
    メイン処理
    """
    # ./sourceディレクトリの存在確認
    if not os.path.exists('./source'):
        print("エラー: ./sourceディレクトリが見つかりません")
        return
    
    # RDFファイルの読み込み
    merged_graph = load_rdf_files('./source')
    
    if len(merged_graph) == 0:
        print("警告: 読み込まれたRDFデータがありません")
        return
    
    # 基本的な統計情報を表示
    print("\n=== データ統計 ===")
    
    # 名前空間の定義
    dcndl = Namespace("http://ndl.go.jp/dcndl/terms/")
    rcgs = Namespace("https://collection.rcgs.jp/terms/")
    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    
    # 各タイプの数をカウント
    bib_resources = list(merged_graph.subjects(RDF.type, dcndl.BibResource))
    print(f"BibResource数: {len(bib_resources)}")
    
    items = list(merged_graph.subjects(RDF.type, dcndl.Item))
    print(f"Item数: {len(items)}")
    
    packages = list(merged_graph.subjects(RDF.type, rcgs.Package))
    print(f"Package数: {len(packages)}")
    
    persons = list(merged_graph.subjects(RDF.type, foaf.Person))
    print(f"Person数: {len(persons)}")
    
    organizations = list(merged_graph.subjects(RDF.type, foaf.Organization))
    print(f"Organization数: {len(organizations)}")
    
    variations = list(merged_graph.subjects(RDF.type, rcgs.Variation))
    print(f"Variation数: {len(variations)}")
    
    works = list(merged_graph.subjects(RDF.type, rcgs.Work))
    print(f"Work数: {len(works)}")
    
    # 使用されている名前空間を表示
    print("\n使用されている名前空間:")
    for prefix, namespace in merged_graph.namespaces():
        print(f"  {prefix}: {namespace}")
    
    # 各データタイプの抽出とCSV保存
    print("\n=== CSV出力開始 ===")
    
    # ゲームパッケージデータの抽出とCSV保存
    df_packages = extract_game_package_data(merged_graph)
    if df_packages is not None:
        save_to_csv(df_packages, 'game_packages.csv')
    
    # 個別資料データの抽出とCSV保存
    df_items = extract_item_data(merged_graph)
    if df_items is not None:
        save_to_csv(df_items, 'items.csv')
    
    # 個人データの抽出とCSV保存
    df_persons = extract_person_data(merged_graph)
    if df_persons is not None:
        save_to_csv(df_persons, 'persons.csv')
    
    # 団体データの抽出とCSV保存
    df_organizations = extract_organization_data(merged_graph)
    if df_organizations is not None:
        save_to_csv(df_organizations, 'organizations.csv')
    
    # バリエーションデータの抽出とCSV保存
    df_variations = extract_variation_data(merged_graph)
    if df_variations is not None:
        save_to_csv(df_variations, 'variations.csv')
    
    # 作品データの抽出とCSV保存
    df_works = extract_work_data(merged_graph)
    if df_works is not None:
        save_to_csv(df_works, 'works.csv')
    
    # 関連資料データの抽出とCSV保存
    df_related_items = extract_related_item_data(merged_graph)
    if df_related_items is not None:
        save_to_csv(df_related_items, 'related_items.csv')
    
    print("\n処理が完了しました。")

if __name__ == "__main__":
    main()
