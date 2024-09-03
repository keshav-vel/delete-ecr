import boto3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def list_and_filter_ecr_repositories(filter_string, region_name='ap-south-1'):
    logging.info(f"Listing ECR repositories in region: {
                 region_name} with filter: {filter_string}")

    ecr_client = boto3.client('ecr', region_name=region_name)
    paginator = ecr_client.get_paginator('describe_repositories')
    filtered_repositories = []

    for page in paginator.paginate():
        for repo in page['repositories']:
            repo_name = repo['repositoryName']
            if filter_string in repo_name:
                filtered_repositories.append(repo_name)
                logging.info(f"Filtered Repository: {repo_name}")

    return filtered_repositories


def delete_ecr_repository(repository_name, region_name='ap-south-1'):
    logging.info(f"Attempting to delete repository: {
                 repository_name} in region: {region_name}")

    ecr_client = boto3.client('ecr', region_name=region_name)
    try:
        delete_all_images_in_repo(repository_name, ecr_client)

        ecr_client.delete_repository(
            repositoryName=repository_name, force=True)
        logging.info(f"Repository '{repository_name}' deleted successfully.")
    except Exception as e:
        logging.error(f"Failed to delete repository '{
                      repository_name}': {str(e)}")


def delete_all_images_in_repo(repository_name, ecr_client):
    logging.info(f"Deleting all images from repository: {repository_name}")

    response = ecr_client.list_images(repositoryName=repository_name)
    image_ids = response.get('imageIds', [])

    if image_ids:
        ecr_client.batch_delete_image(
            repositoryName=repository_name, imageIds=image_ids)
        logging.info(f"All images deleted from repository '{
                     repository_name}'.")


if __name__ == "__main__":
    # SET PREFIX HERE
    filter_str = "ci-gurukul"
    region = "ap-south-1"

    repositories_to_delete = list_and_filter_ecr_repositories(
        filter_string=filter_str, region_name=region)

    for repo in repositories_to_delete:
        delete_ecr_repository(repository_name=repo, region_name=region)
