import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    """
    Implements the 8 Data Cleaning Steps & Feature Engineering Pipeline:
    1. Load Data
    2. Explore Data (Types, Summary Stats, Issues)
    3. Handle Missing Values (Impute/Remove)
    4. Remove Duplicates
    5. Handle Outliers (IQR / Z-score capping or removal)
    6. Encode Categorical Data (Label / One-Hot)
    7. Scale Numerical Features (MinMax / Standard)
    8. Final Validation Check & Export
    """
    
    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.raw_df: Optional[pd.DataFrame] = df.copy() if df is not None else None
        self.cleaned_df: Optional[pd.DataFrame] = df.copy() if df is not None else None
        self.encoded_df: Optional[pd.DataFrame] = None
        self.scaled_df: Optional[pd.DataFrame] = None
        self.stats_log: List[Dict[str, Any]] = []

    def load_data(self, filepath_or_df) -> pd.DataFrame:
        """Step 1: Load Data"""
        if isinstance(filepath_or_df, (str, Path)):
            self.raw_df = pd.read_csv(filepath_or_df)
        elif isinstance(filepath_or_df, pd.DataFrame):
            self.raw_df = filepath_or_df.copy()
        else:
            raise ValueError("Invalid dataset input format")
        
        self.cleaned_df = self.raw_df.copy()
        self.stats_log.append({
            "step": "1_load_data",
            "rows": len(self.raw_df),
            "columns": len(self.raw_df.columns),
            "col_names": list(self.raw_df.columns)
        })
        return self.raw_df

    def explore_data(self) -> Dict[str, Any]:
        """Step 2: Explore Data"""
        if self.raw_df is None:
            raise ValueError("Data not loaded yet.")
        
        missing_counts = self.raw_df.isnull().sum().to_dict()
        duplicate_count = int(self.raw_df.duplicated().sum())
        data_types = {col: str(dtype) for col, dtype in self.raw_df.dtypes.items()}
        
        num_summary = {}
        numeric_cols = self.raw_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            num_summary[col] = {
                "mean": float(self.raw_df[col].mean()),
                "std": float(self.raw_df[col].std()),
                "min": float(self.raw_df[col].min()),
                "25%": float(self.raw_df[col].quantile(0.25)),
                "50%": float(self.raw_df[col].median()),
                "75%": float(self.raw_df[col].quantile(0.75)),
                "max": float(self.raw_df[col].max())
            }

        exploration = {
            "total_rows": len(self.raw_df),
            "total_columns": len(self.raw_df.columns),
            "data_types": data_types,
            "missing_values": missing_counts,
            "duplicate_count": duplicate_count,
            "numeric_summary": num_summary
        }
        return exploration

    def handle_missing_values(self, strategy: str = "impute_mean") -> int:
        """Step 3: Handle Missing Values"""
        if self.cleaned_df is None:
            return 0
        
        initial_missing = int(self.cleaned_df.isnull().sum().sum())
        if initial_missing == 0:
            return 0

        if strategy == "drop":
            self.cleaned_df.dropna(inplace=True)
        elif strategy in ["impute_mean", "impute_median"]:
            numeric_cols = self.cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self.cleaned_df[col].isnull().sum() > 0:
                    val = self.cleaned_df[col].mean() if strategy == "impute_mean" else self.cleaned_df[col].median()
                    self.cleaned_df[col].fillna(val, inplace=True)
            
            categorical_cols = self.cleaned_df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                if self.cleaned_df[col].isnull().sum() > 0:
                    mode_val = self.cleaned_df[col].mode()[0] if len(self.cleaned_df[col].mode()) > 0 else "Unknown"
                    self.cleaned_df[col].fillna(mode_val, inplace=True)

        return initial_missing

    def remove_duplicates(self) -> int:
        """Step 4: Remove Duplicates"""
        if self.cleaned_df is None:
            return 0
        dup_count = int(self.cleaned_df.duplicated().sum())
        if dup_count > 0:
            self.cleaned_df.drop_duplicates(inplace=True)
            self.cleaned_df.reset_index(drop=True, inplace=True)
        return dup_count

    def handle_outliers(self, method: str = "iqr", threshold: float = 1.5, action: str = "cap") -> Dict[str, int]:
        """Step 5: Handle Outliers (IQR or Z-Score capping/removal)"""
        if self.cleaned_df is None:
            return {}
        
        outliers_detected = {}
        numeric_cols = self.cleaned_df.select_dtypes(include=[np.number]).columns
        
        # Exclude IDs or binary columns from outlier treatment
        skip_cols = ['Container_ID', 'Job_ID', 'Tenant_ID', 'Server_ID', 'Optimal_Scheduling']
        target_cols = [col for col in numeric_cols if col not in skip_cols]

        for col in target_cols:
            if method == "iqr":
                q1 = self.cleaned_df[col].quantile(0.25)
                q3 = self.cleaned_df[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
            else: # zscore
                mean = self.cleaned_df[col].mean()
                std = self.cleaned_df[col].std()
                lower = mean - threshold * std
                upper = mean + threshold * std
            
            is_outlier = (self.cleaned_df[col] < lower) | (self.cleaned_df[col] > upper)
            count = int(is_outlier.sum())
            outliers_detected[col] = count
            
            if count > 0 and action == "cap":
                self.cleaned_df[col] = np.clip(self.cleaned_df[col], lower, upper)
        
        if action == "drop":
            condition = pd.Series(True, index=self.cleaned_df.index)
            for col in target_cols:
                q1 = self.cleaned_df[col].quantile(0.25)
                q3 = self.cleaned_df[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                condition &= (self.cleaned_df[col] >= lower) & (self.cleaned_df[col] <= upper)
            self.cleaned_df = self.cleaned_df[condition].reset_index(drop=True)

        return outliers_detected

    def encode_categorical(self) -> pd.DataFrame:
        """Step 6: Encode Categorical Data"""
        if self.cleaned_df is None:
            raise ValueError("No cleaned data available")
        
        self.encoded_df = self.cleaned_df.copy()
        cat_cols = self.encoded_df.select_dtypes(include=['object', 'category']).columns
        
        for col in cat_cols:
            self.encoded_df[col] = self.encoded_df[col].astype('category').cat.codes

        return self.encoded_df

    def scale_numerical(self, method: str = "minmax") -> pd.DataFrame:
        """Step 7: Scale Numerical Features"""
        df_to_scale = self.encoded_df.copy() if self.encoded_df is not None else self.cleaned_df.copy()
        numeric_cols = df_to_scale.select_dtypes(include=[np.number]).columns
        
        skip_cols = ['Container_ID', 'Job_ID', 'Tenant_ID', 'Server_ID', 'Optimal_Scheduling']
        cols_to_scale = [c for c in numeric_cols if c not in skip_cols]

        self.scaled_df = df_to_scale.copy()
        for col in cols_to_scale:
            min_val = df_to_scale[col].min()
            max_val = df_to_scale[col].max()
            if max_val > min_val:
                if method == "minmax":
                    self.scaled_df[col] = (df_to_scale[col] - min_val) / (max_val - min_val)
                elif method == "standard":
                    mean_val = df_to_scale[col].mean()
                    std_val = df_to_scale[col].std() if df_to_scale[col].std() > 0 else 1.0
                    self.scaled_df[col] = (df_to_scale[col] - mean_val) / std_val

        return self.scaled_df

    def final_check_and_validate(self) -> Dict[str, Any]:
        """Step 8: Final Check & Validation"""
        if self.cleaned_df is None:
            return {"valid": False, "reason": "No data"}

        missing_count = int(self.cleaned_df.isnull().sum().sum())
        duplicate_count = int(self.cleaned_df.duplicated().sum())

        # Derived scheduling fields validation
        neg_cpu = int((self.cleaned_df.get('Requested_CPU_Cores', pd.Series([1])) <= 0).sum())
        neg_mem = int((self.cleaned_df.get('Requested_Memory_MB', pd.Series([1])) <= 0).sum())
        
        is_valid = (missing_count == 0) and (duplicate_count == 0) and (neg_cpu == 0) and (neg_mem == 0)

        validation_report = {
            "valid": is_valid,
            "final_row_count": len(self.cleaned_df),
            "final_col_count": len(self.cleaned_df.columns),
            "remaining_missing_values": missing_count,
            "remaining_duplicates": duplicate_count,
            "invalid_cpu_count": neg_cpu,
            "invalid_memory_count": neg_mem,
            "status": "VALIDATED & READY FOR SIMULATION" if is_valid else "VALIDATION WARNING"
        }
        return validation_report

    def run_full_pipeline(self, filepath_or_df, missing_strategy="impute_mean", outlier_method="iqr", scale_method="minmax") -> Dict[str, Any]:
        """Runs all 8 data cleaning steps end-to-end"""
        self.load_data(filepath_or_df)
        exploration = self.explore_data()
        missing_handled = self.handle_missing_values(strategy=missing_strategy)
        duplicates_removed = self.remove_duplicates()
        outliers_info = self.handle_outliers(method=outlier_method, action="cap")
        encoded_df = self.encode_categorical()
        scaled_df = self.scale_numerical(method=scale_method)
        validation_report = self.final_check_and_validate()

        return {
            "exploration": exploration,
            "missing_values_handled": missing_handled,
            "duplicates_removed": duplicates_removed,
            "outliers_info": outliers_info,
            "validation": validation_report,
            "cleaned_rows": len(self.cleaned_df)
        }
