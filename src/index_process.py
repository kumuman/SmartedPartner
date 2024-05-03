# import torch
import hashlib
import os
import pickle
import re
from collections import defaultdict
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Optional, Any
import pandas as pd

from loguru import logger
from tqdm import tqdm

chunk_size = 500
chunk_overlap = 50


class ChineseRecursiveTextSplitter(RecursiveCharacterTextSplitter):
    """Recursive text splitter for Chinese text.
    copy from: https://github.com/chatchat-space/Langchain-Chatchat/tree/master
    """

    def __init__(
            self,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True,
            is_separator_regex: bool = True,
            **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or [
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s"
        ]
        self._is_separator_regex = is_separator_regex

    @staticmethod
    def _split_text_with_regex_from_end(
            text: str, separator: str, keep_separator: bool
    ) -> List[str]:
        # Now that we have the separator, split the text
        if separator:
            if keep_separator:
                # The parentheses in the pattern keep the delimiters in the result.
                _splits = re.split(f"({separator})", text)
                splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
                if len(_splits) % 2 == 1:
                    splits += _splits[-1:]
            else:
                splits = re.split(separator, text)
        else:
            splits = list(text)
        return [s for s in splits if s != ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = self._split_text_with_regex_from_end(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip() != ""]


def load_embedding_mode(model_name='text2vec'):
    # if torch.cuda.is_available():
    #     model_kwargs = {'device': 'cuda'}
    # else:
    #     model_kwargs = {'device':'cpu'}
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return hf


def sheet_to_string(sheet, sheet_name=None):
    result = []
    for index, row in sheet.iterrows():
        row_string = ""
        for column in sheet.columns:
            row_string += f"{column}: {row[column]}, "
        row_string = row_string.rstrip(", ")
        row_string += "."
        result.append(row_string)
    return result


def excel_to_string(file_path):
    # 读取Excel文件中的所有工作表
    excel_file = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)

    # 初始化结果字符串
    result = []

    # 遍历每一个工作表
    for sheet_name, sheet_data in excel_file.items():
        # 处理当前工作表并添加到结果字符串
        result += sheet_to_string(sheet_data, sheet_name=sheet_name)

    return result


def update_doc_config(two_column_pdf):
    global advance_docs
    advance_docs["pdf"]["two_column"] = two_column_pdf


def get_documents(files):
    text_splitter = ChineseRecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    documents = []
    logger.debug("Loading documents...")
    logger.debug(f"file_paths: {os.path.basename(files.name)}")
    _, file_extension = os.path.splitext(files.name)
    # 去除扩展名前的点号
    file_type = file_extension[1:]
    file_paths = files.name
    texts = None
    try:
        if file_type == ".pdf":
            import PyPDF2
            logger.debug("Loading PDF...")
            try:
                from pdf_func import parse_pdf

                config = {}
                advance_docs = defaultdict(lambda: defaultdict(dict))
                advance_docs.update(config.get("advance_docs", {}))

                two_column = advance_docs["pdf"].get("two_column", False)
                pdftext = parse_pdf(file_paths, two_column).text
            except:
                pdftext = ""
                with open(file_paths, "rb") as pdfFileObj:
                    pdfReader = PyPDF2.PdfReader(pdfFileObj)
                    for page in tqdm(pdfReader.pages):
                        pdftext += page.extract_text()
            texts = [Document(page_content=pdftext,
                              metadata={"source": file_paths})]
        elif file_type == ".docx":
            logger.debug("Loading Word...")
            from langchain.document_loaders import UnstructuredWordDocumentLoader
            loader = UnstructuredWordDocumentLoader(file_paths)
            texts = loader.load()
        elif file_type == ".pptx":
            logger.debug("Loading PowerPoint...")
            from langchain.document_loaders import UnstructuredPowerPointLoader
            loader = UnstructuredPowerPointLoader(file_paths)
            texts = loader.load()
        elif file_type == ".epub":
            logger.debug("Loading EPUB...")
            from langchain.document_loaders import UnstructuredEPubLoader
            loader = UnstructuredEPubLoader(file_paths)
            texts = loader.load()
        elif file_type == ".xlsx":
            logger.debug("Loading Excel...")
            text_list = excel_to_string(file_paths)
            texts = []
            for elem in text_list:
                texts.append(Document(page_content=elem,
                                      metadata={"source": file_paths}))
        else:
            logger.debug("Loading text file...")
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_paths, "utf8")
            texts = loader.load()
        # logger.debug(f"text size: {len(texts)}, text top3: {texts[:3]}")
    except Exception as e:
        logger.error(f"Error loading file: {file_paths}, {e}")

    if texts is not None:
        texts = text_splitter.split_documents(texts)
        documents.extend(texts)
    logger.debug(f"Documents loaded. documents size: {len(documents)}, top3: {documents[:3]}")
    return documents


def construct_index(files):
    embeddings = load_embedding_mode(model_name='text2vec')
    filename, _ = os.path.splitext(os.path.basename(files.name))
    logger.debug(f'files_absolute_name:{files.name}')
    logger.debug(f'files_simple_name:{filename}')
    try:
        if os.path.exists("indexs/" + filename):
            logger.info("加载索引...")
            index = FAISS.load_local("indexs/" + filename, embeddings=embeddings, allow_dangerous_deserialization=True)
        else:
            documents = get_documents(files)
            logger.info("构建索引中……")
            index = FAISS.from_documents(documents, embeddings)
            logger.debug("索引构建完成！")
            index.save_local("indexs/" + filename)
        return index
    except Exception as e:
        logger.error(f"索引构建失败！error: {e}")
        return None


def save_pkl(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def get_files_hash(file_src=None, file_paths=None):
    if file_src:
        file_paths = [x.name for x in file_src]
    file_paths.sort(key=lambda x: os.path.basename(x))

    md5_hash = hashlib.md5()
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)

    return md5_hash.hexdigest()
